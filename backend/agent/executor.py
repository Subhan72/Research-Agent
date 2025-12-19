"""Tool executor for orchestrating tool execution sequentially."""
from typing import Dict, Any, List, Optional
from backend.tools.web_search import WebSearchTool
from backend.tools.scraper import WebScraperTool
from backend.tools.data_analysis import DataAnalysisTool
from backend.tools.calculator import CalculatorTool
from backend.tools.summarizer import SummarizerTool
from backend.utils.llm_client import GroqClient


class ToolExecutor:
    """Executes tools sequentially based on a plan."""
    
    def __init__(self):
        """Initialize executor with all available tools."""
        self.tools = {
            'web_search': WebSearchTool(),
            'scraper': WebScraperTool(),
            'data_analysis': DataAnalysisTool(),
            'calculator': CalculatorTool(),
            'summarizer': SummarizerTool(llm_client=GroqClient())
        }
    
    def execute_tool(
        self,
        tool_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a single tool.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool-specific arguments
            
        Returns:
            Dictionary with tool execution results
        """
        if tool_name not in self.tools:
            return {
                'tool': tool_name,
                'success': False,
                'error': f'Unknown tool: {tool_name}'
            }
        
        try:
            tool = self.tools[tool_name]
            
            # Route to appropriate tool method
            if tool_name == 'web_search':
                query = kwargs.get('query', '')
                result = tool.search(query)
            elif tool_name == 'scraper':
                url = kwargs.get('url', '')
                result = tool.scrape(url)
            elif tool_name == 'data_analysis':
                text = kwargs.get('text')
                data = kwargs.get('data')
                create_chart = kwargs.get('create_chart', False)
                result = tool.analyze(text=text, data=data, create_chart=create_chart)
            elif tool_name == 'calculator':
                expression = kwargs.get('expression', '')
                result = tool.calculate(expression)
            elif tool_name == 'summarizer':
                text = kwargs.get('text', '')
                max_length = kwargs.get('max_length')
                style = kwargs.get('style', 'concise')
                result = tool.summarize(text, max_length=max_length, style=style)
            else:
                return {
                    'tool': tool_name,
                    'success': False,
                    'error': f'Tool execution not implemented: {tool_name}'
                }
            
            return {
                'tool': tool_name,
                'success': True,
                'result': result
            }
            
        except Exception as e:
            return {
                'tool': tool_name,
                'success': False,
                'error': str(e)
            }
    
    def execute_plan(
        self,
        plan: Dict[str, Any],
        sub_questions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Execute a complete research plan.
        
        Args:
            plan: Research plan with tool_sequence
            sub_questions: List of sub-questions to research
            
        Returns:
            Dictionary with all tool execution results
        """
        tool_sequence = plan.get('tool_sequence', [])
        sub_questions = sub_questions or plan.get('sub_questions', [])
        
        all_results = {
            'plan': plan,
            'tool_results': [],
            'success': True,
            'errors': []
        }
        
        # Track URLs found from search for scraping
        urls_to_scrape = []
        
        # Limit sub-questions for faster processing
        import config
        limited_sub_questions = sub_questions[:config.MAX_SUB_QUESTIONS] if hasattr(config, 'MAX_SUB_QUESTIONS') else sub_questions[:5]
        
        # Execute tools in sequence
        for tool_name in tool_sequence:
            tool_result = None
            
            if tool_name == 'web_search':
                # Search for limited sub-questions (or main query if too many)
                search_results = []
                if len(limited_sub_questions) > 3:
                    # If too many sub-questions, just search the main query
                    result = self.execute_tool('web_search', query=plan.get('query', limited_sub_questions[0]))
                    search_results.append(result)
                    
                    if result.get('success') and 'result' in result:
                        search_data = result['result']
                        if 'results' in search_data:
                            for item in search_data.get('results', []):
                                if 'url' in item:
                                    urls_to_scrape.append(item['url'])
                else:
                    # Search for each sub-question (limited)
                    for question in limited_sub_questions:
                        result = self.execute_tool('web_search', query=question)
                        search_results.append(result)
                        
                        # Collect URLs for scraping
                        if result.get('success') and 'result' in result:
                            search_data = result['result']
                            if 'results' in search_data:
                                for item in search_data.get('results', []):
                                    if 'url' in item:
                                        urls_to_scrape.append(item['url'])
                
                all_results['tool_results'].extend(search_results)
            
            elif tool_name == 'scraper':
                # Scrape URLs found from search (limited)
                import config
                max_urls = config.MAX_URLS_TO_SCRAPE if hasattr(config, 'MAX_URLS_TO_SCRAPE') else 3
                scrape_results = []
                for url in urls_to_scrape[:max_urls]:  # Limit URLs
                    result = self.execute_tool('scraper', url=url)
                    scrape_results.append(result)
                    # Break early if we have enough successful scrapes
                    successful = sum(1 for r in scrape_results if r.get('success'))
                    if successful >= 2:  # Stop after 2 successful scrapes
                        break
                
                all_results['tool_results'].extend(scrape_results)
            
            elif tool_name == 'data_analysis':
                # Analyze scraped content
                # Collect all text from previous results
                text_to_analyze = ""
                for prev_result in all_results['tool_results']:
                    if prev_result.get('tool') == 'scraper' and prev_result.get('success'):
                        scraped = prev_result.get('result', {})
                        text_to_analyze += scraped.get('text', '') + " "
                
                if text_to_analyze:
                    tool_result = self.execute_tool(
                        'data_analysis',
                        text=text_to_analyze,
                        create_chart=True
                    )
                    all_results['tool_results'].append(tool_result)
            
            elif tool_name == 'summarizer':
                # Summarize key findings
                # Collect text from scraped content (limited)
                text_to_summarize = ""
                for prev_result in all_results['tool_results']:
                    if prev_result.get('tool') == 'scraper' and prev_result.get('success'):
                        scraped = prev_result.get('result', {})
                        text = scraped.get('text', '')
                        # Limit each scraped text to 2000 chars
                        text_to_summarize += text[:2000] + "\n\n"
                        # Stop after collecting enough text
                        if len(text_to_summarize) > 3000:
                            break
                
                if text_to_summarize:
                    tool_result = self.execute_tool(
                        'summarizer',
                        text=text_to_summarize[:3000],  # Further limit length
                        max_length=150,  # Shorter summary
                        style='concise'  # Faster concise style
                    )
                    all_results['tool_results'].append(tool_result)
            
            else:
                # Generic tool execution
                tool_result = self.execute_tool(tool_name)
                all_results['tool_results'].append(tool_result)
            
            # Check for errors (only if tool_result was set)
            if tool_result and not tool_result.get('success'):
                all_results['errors'].append({
                    'tool': tool_name,
                    'error': tool_result.get('error', 'Unknown error')
                })
        
        return all_results

