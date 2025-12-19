"""Main research agent that orchestrates planning, execution, and synthesis."""
from typing import Dict, Any, Optional
from backend.agent.planner import Planner
from backend.agent.executor import ToolExecutor
from backend.agent.synthesizer import Synthesizer
from backend.storage.cache import JSONCache
from backend.storage.vector_store import VectorStore
from backend.utils.llm_client import GroqClient


class ResearchAgent:
    """Complete research agent that plans, executes, and synthesizes research."""
    
    def __init__(self):
        """Initialize research agent with all components."""
        llm_client = GroqClient()
        self.planner = Planner(llm_client=llm_client)
        self.executor = ToolExecutor()
        self.synthesizer = Synthesizer(llm_client=llm_client)
        self.cache = JSONCache()
        self.vector_store = VectorStore()
    
    def research(
        self,
        query: str,
        use_cache: bool = True,
        generate_pdf: bool = False
    ) -> Dict[str, Any]:
        """Perform complete research workflow.
        
        Args:
            query: Research query
            use_cache: Whether to use cached results
            generate_pdf: Whether to generate PDF report
            
        Returns:
            Dictionary with complete research results including:
            - plan: Research plan
            - tool_results: Tool execution results
            - report: Generated report
            - pdf_path: PDF path if generated
        """
        # Check vector store for similar queries
        if use_cache:
            similar = self.vector_store.search(query, n_results=1)
            if similar and similar[0].get('distance', 1.0) < 0.3:  # Similarity threshold
                # Use cached result
                cached_metadata = similar[0].get('metadata', {})
                # Could return cached result here
        
        # Step 1: Planning
        plan = self.planner.create_plan(query)
        
        # Step 2: Execution
        execution_results = self.executor.execute_plan(plan, plan.get('sub_questions'))
        
        # Step 3: Synthesis
        report = self.synthesizer.generate_report(
            query=query,
            plan=plan,
            tool_results=execution_results.get('tool_results', [])
        )
        
        # Step 4: Generate PDF if requested
        pdf_result = None
        if generate_pdf:
            pdf_result = self.synthesizer.markdown_to_pdf(report.get('markdown', ''))
        
        # Store in vector store for future reference
        try:
            self.vector_store.add(
                query=query,
                results={
                    'plan': plan,
                    'execution': execution_results,
                    'report': report
                }
            )
        except Exception:
            pass  # Silently fail if vector store fails
        
        return {
            'query': query,
            'plan': plan,
            'tool_results': execution_results.get('tool_results', []),
            'report': report,
            'pdf': pdf_result,
            'success': True
        }
    
    def research_streaming(
        self,
        query: str,
        use_cache: bool = True
    ):
        """Perform research with streaming updates (generator).
        
        Args:
            query: Research query
            use_cache: Whether to use cached results
            
        Yields:
            Dictionary updates for each step of the process
        """
        # Step 1: Planning
        yield {'step': 'planning', 'status': 'in_progress'}
        plan = self.planner.create_plan(query)
        yield {'step': 'planning', 'status': 'completed', 'data': plan}
        
        # Step 2: Execution (stream tool results)
        yield {'step': 'execution', 'status': 'in_progress'}
        execution_results = self.executor.execute_plan(plan, plan.get('sub_questions'))
        
        # Yield each tool result
        for tool_result in execution_results.get('tool_results', []):
            yield {'step': 'tool_result', 'data': tool_result}
        
        yield {'step': 'execution', 'status': 'completed', 'data': execution_results}
        
        # Step 3: Synthesis
        yield {'step': 'synthesis', 'status': 'in_progress'}
        report = self.synthesizer.generate_report(
            query=query,
            plan=plan,
            tool_results=execution_results.get('tool_results', [])
        )
        yield {'step': 'synthesis', 'status': 'completed', 'data': report}
        
        # Final result
        yield {
            'step': 'complete',
            'query': query,
            'plan': plan,
            'tool_results': execution_results.get('tool_results', []),
            'report': report,
            'success': True
        }

