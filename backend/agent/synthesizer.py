"""Synthesizer module for generating structured research reports."""
from typing import Dict, Any, List, Optional
from pathlib import Path
import config
from backend.utils.llm_client import GroqClient


class Synthesizer:
    """Generates structured research reports from tool results."""
    
    def __init__(self, llm_client: Optional[GroqClient] = None):
        """Initialize synthesizer.
        
        Args:
            llm_client: Groq client instance. If None, creates new one
        """
        self.llm = llm_client or GroqClient()
    
    def extract_citations(self, tool_results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract citations from tool results.
        
        Args:
            tool_results: List of tool execution results
            
        Returns:
            List of citations with title and URL
        """
        citations = []
        seen_urls = set()
        
        for result in tool_results:
            if not result.get('success'):
                continue
            
            tool_name = result.get('tool', '')
            tool_data = result.get('result', {})
            
            if tool_name == 'web_search':
                # Extract from search results
                search_results = tool_data.get('results', [])
                for item in search_results:
                    url = item.get('url', '')
                    title = item.get('title', '')
                    if url and url not in seen_urls:
                        citations.append({
                            'title': title or url,
                            'url': url
                        })
                        seen_urls.add(url)
            
            elif tool_name == 'scraper':
                # Extract from scraped pages
                url = tool_data.get('url', '')
                title = tool_data.get('title', '')
                if url and url not in seen_urls:
                    citations.append({
                        'title': title or url,
                        'url': url
                    })
                    seen_urls.add(url)
        
        return citations
    
    def generate_report(
        self,
        query: str,
        plan: Dict[str, Any],
        tool_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a structured research report.
        
        Args:
            query: Original research query
            plan: Research plan
            tool_results: Results from tool execution
            
        Returns:
            Dictionary with markdown report and metadata
        """
        # Extract citations
        citations = self.extract_citations(tool_results)
        
        # Collect all information from tool results
        search_info = []
        scraped_content = []
        data_analysis = None
        summaries = []
        
        for result in tool_results:
            if not result.get('success'):
                continue
            
            tool_name = result.get('tool', '')
            tool_data = result.get('result', {})
            
            if tool_name == 'web_search':
                search_info.append(tool_data)
            elif tool_name == 'scraper':
                scraped_content.append(tool_data)
            elif tool_name == 'data_analysis':
                data_analysis = tool_data
            elif tool_name == 'summarizer':
                summaries.append(tool_data)
        
        # Build context for LLM
        context_parts = []
        
        # Add search results
        for search in search_info:
            if 'results' in search:
                context_parts.append(f"Search Results:\n{str(search['results'][:3])}")
        
        # Add scraped content (summarized)
        for scraped in scraped_content[:3]:  # Limit to 3
            if 'text' in scraped:
                text = scraped['text'][:1000]  # Limit length
                context_parts.append(f"Content from {scraped.get('title', 'page')}:\n{text}")
        
        # Add data analysis
        if data_analysis:
            context_parts.append(f"Data Analysis:\n{str(data_analysis)}")
        
        context = "\n\n".join(context_parts)
        
        # Generate report using LLM
        system_prompt = """You are a research report writer. Create a comprehensive, well-structured research report based on the provided information. The report should be professional, accurate, and well-organized."""
        
        prompt = f"""Based on the following research query and collected information, create a comprehensive research report in Markdown format.

Research Query: {query}

Collected Information:
{context}

Create a report with the following structure:
1. # Title (based on the query)
2. ## Executive Summary (2-3 paragraphs)
3. ## Key Findings (bullet points of main findings)
4. ## Deep Dive (detailed sections covering different aspects)
5. ## Data Analysis (if data was found, include tables/charts descriptions)
6. ## Conclusion (summary and implications)
7. ## References (list all source URLs)

Make sure to:
- Synthesize information from multiple sources
- Provide accurate information
- Include specific details and numbers when available
- Write in a professional, academic style
- Cite sources naturally in the text
- Format the report properly in Markdown"""
        
        try:
            markdown_report = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=min(config.MAX_RESPONSE_TOKENS * 2, 3000),  # Cap at 3000 tokens
                temperature=0.7
            )
            
            # Ensure references section exists
            if "## References" not in markdown_report and citations:
                markdown_report += "\n\n## References\n\n"
                for i, citation in enumerate(citations, 1):
                    markdown_report += f"{i}. [{citation['title']}]({citation['url']})\n"
            
            return {
                'query': query,
                'markdown': markdown_report,
                'citations': citations,
                'success': True
            }
            
        except Exception as e:
            # Fallback report
            markdown_report = f"""# Research Report: {query}

## Executive Summary

Research was conducted on: {query}

## Key Findings

- Information gathered from {len(citations)} sources
- Multiple perspectives analyzed

## Deep Dive

{context[:2000]}

## Conclusion

Research completed with findings from various sources.

## References

"""
            for i, citation in enumerate(citations, 1):
                markdown_report += f"{i}. [{citation['title']}]({citation['url']})\n"
            
            return {
                'query': query,
                'markdown': markdown_report,
                'citations': citations,
                'success': False,
                'error': str(e)
            }
    
    def markdown_to_pdf(self, markdown_text: str, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """Convert Markdown report to PDF.
        
        Args:
            markdown_text: Markdown text to convert
            output_path: Output file path. If None, generates temporary path
            
        Returns:
            Dictionary with PDF path and metadata
        """
        try:
            import markdown
            from weasyprint import HTML, CSS
            from io import StringIO
            
            # Convert markdown to HTML
            html = markdown.markdown(
                markdown_text,
                extensions=['extra', 'codehilite', 'tables']
            )
            
            # Add basic styling
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    h1 {{ color: #333; border-bottom: 2px solid #333; }}
                    h2 {{ color: #555; margin-top: 30px; }}
                    h3 {{ color: #777; }}
                    code {{ background: #f4f4f4; padding: 2px 4px; }}
                    pre {{ background: #f4f4f4; padding: 10px; overflow-x: auto; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                {html}
            </body>
            </html>
            """
            
            # Generate output path if not provided
            if output_path is None:
                import hashlib
                report_hash = hashlib.md5(markdown_text.encode()).hexdigest()[:8]
                output_path = Path(config.CACHE_DIR) / f"report_{report_hash}.pdf"
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert HTML to PDF
            HTML(string=styled_html).write_pdf(str(output_path))
            
            return {
                'success': True,
                'path': str(output_path),
                'size': output_path.stat().st_size if output_path.exists() else 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

