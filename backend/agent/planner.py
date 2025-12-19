"""Planner module for breaking queries into sub-questions and creating execution plans."""
from typing import Dict, Any, List, Optional
import config
from backend.utils.llm_client import GroqClient
from backend.utils.validators import sanitize_query


class Planner:
    """Plans research by breaking queries into sub-questions and tool sequences."""
    
    def __init__(self, llm_client: Optional[GroqClient] = None):
        """Initialize planner.
        
        Args:
            llm_client: Groq client instance. If None, creates new one
        """
        self.llm = llm_client or GroqClient()
    
    def create_plan(self, query: str) -> Dict[str, Any]:
        """Create a research plan from user query.
        
        Args:
            query: User research query
            
        Returns:
            Dictionary with:
            - query: Original query
            - sub_questions: List of sub-questions (3-7)
            - tool_sequence: Ordered list of tools to execute
            - plan: Structured plan object
        """
        query = sanitize_query(query)
        
        # Create planning prompt
        system_prompt = """You are a research planning assistant. Break down research queries into 3-7 focused sub-questions that can be answered through web search and analysis. Determine which tools are needed for each sub-question.

Available tools:
- web_search: Search the internet for information
- scraper: Extract content from webpages
- data_analysis: Analyze numbers and create charts
- calculator: Perform mathematical calculations
- summarizer: Summarize long texts

Respond with a JSON object containing:
- sub_questions: array of 3-7 sub-questions
- tool_sequence: array of tool names in execution order
- reasoning: brief explanation of the plan"""
        
        prompt = f"""Break down this research query into sub-questions and create an execution plan:

Query: {query}

Provide a JSON response with:
1. sub_questions: 3-7 focused sub-questions
2. tool_sequence: ordered list of tools needed (e.g., ["web_search", "scraper", "data_analysis"])
3. reasoning: brief explanation of why this plan will work"""
        
        try:
            plan_json = self.llm.generate_json(prompt, system_prompt)
            
            # Validate and structure plan
            sub_questions = plan_json.get('sub_questions', [])
            if not sub_questions or len(sub_questions) < 3:
                # Fallback: create simple plan
                sub_questions = [
                    f"What is {query}?",
                    f"What are the key aspects of {query}?",
                    f"What are recent developments regarding {query}?"
                ]
            
            tool_sequence = plan_json.get('tool_sequence', ['web_search', 'scraper'])
            if not tool_sequence:
                tool_sequence = ['web_search', 'scraper']
            
            reasoning = plan_json.get('reasoning', 'Standard research plan')
            
            # Limit sub-questions to 5 for faster processing
            import config
            max_sub_questions = config.MAX_SUB_QUESTIONS if hasattr(config, 'MAX_SUB_QUESTIONS') else 5
            return {
                'query': query,
                'sub_questions': sub_questions[:max_sub_questions],
                'tool_sequence': tool_sequence,
                'reasoning': reasoning,
                'success': True
            }
            
        except Exception as e:
            # Fallback plan on error
            return {
                'query': query,
                'sub_questions': [
                    f"What is {query}?",
                    f"What are the key aspects of {query}?",
                    f"What are recent developments regarding {query}?"
                ],
                'tool_sequence': ['web_search', 'scraper', 'summarizer'],
                'reasoning': 'Fallback plan due to planning error',
                'success': False,
                'error': str(e)
            }

