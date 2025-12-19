"""Unit tests for agent components."""
import unittest
from unittest.mock import Mock, patch, MagicMock
from backend.agent.planner import Planner
from backend.agent.executor import ToolExecutor


class TestPlanner(unittest.TestCase):
    """Test planner module."""
    
    @patch('backend.agent.planner.GroqClient')
    def test_create_plan(self, mock_groq):
        """Test plan creation."""
        # Mock LLM response
        mock_client = MagicMock()
        mock_client.generate_json.return_value = {
            'sub_questions': [
                'What is AI?',
                'How does AI work?',
                'What are AI applications?'
            ],
            'tool_sequence': ['web_search', 'scraper'],
            'reasoning': 'Test reasoning'
        }
        mock_groq.return_value = mock_client
        
        planner = Planner(llm_client=mock_client)
        plan = planner.create_plan("Artificial Intelligence")
        
        self.assertIn('sub_questions', plan)
        self.assertIn('tool_sequence', plan)
        self.assertGreaterEqual(len(plan['sub_questions']), 3)


class TestExecutor(unittest.TestCase):
    """Test executor module."""
    
    def setUp(self):
        self.executor = ToolExecutor()
    
    @patch('backend.tools.web_search.WebSearchTool')
    def test_execute_web_search(self, mock_search_tool):
        """Test web search execution."""
        mock_tool = MagicMock()
        mock_tool.search.return_value = {
            'results': [{'title': 'Test', 'url': 'http://test.com'}],
            'query': 'test',
            'total_results': 1
        }
        mock_search_tool.return_value = mock_tool
        
        result = self.executor.execute_tool('web_search', query='test query')
        self.assertIn('success', result)
    
    def test_execute_unknown_tool(self):
        """Test execution of unknown tool."""
        result = self.executor.execute_tool('unknown_tool')
        self.assertFalse(result['success'])
        self.assertIn('error', result)


if __name__ == '__main__':
    unittest.main()

