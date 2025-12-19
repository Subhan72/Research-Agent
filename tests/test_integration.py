"""Integration tests for complete research workflow."""
import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestIntegration(unittest.TestCase):
    """Integration tests for research agent."""
    
    @patch('backend.agent.research_agent.GroqClient')
    @patch('backend.agent.research_agent.WebSearchTool')
    @patch('backend.agent.research_agent.WebScraperTool')
    def test_research_workflow(self, mock_scraper, mock_search, mock_groq):
        """Test complete research workflow with mocked dependencies."""
        # Mock Groq client
        mock_llm = MagicMock()
        mock_llm.generate_json.return_value = {
            'sub_questions': ['Question 1', 'Question 2', 'Question 3'],
            'tool_sequence': ['web_search', 'scraper'],
            'reasoning': 'Test'
        }
        mock_llm.generate.return_value = "# Test Report\n\nTest content."
        mock_groq.return_value = mock_llm
        
        # Mock search tool
        mock_search_instance = MagicMock()
        mock_search_instance.search.return_value = {
            'results': [{'title': 'Test', 'url': 'http://test.com', 'snippet': 'Test snippet'}],
            'query': 'test',
            'total_results': 1
        }
        mock_search.return_value = mock_search_instance
        
        # Mock scraper tool
        mock_scraper_instance = MagicMock()
        mock_scraper_instance.scrape.return_value = {
            'url': 'http://test.com',
            'title': 'Test Page',
            'text': 'Test content here.',
            'length': 20,
            'success': True
        }
        mock_scraper.return_value = mock_scraper_instance
        
        # Import and test agent
        from backend.agent.research_agent import ResearchAgent
        
        agent = ResearchAgent()
        # Note: This would require actual API keys in real scenario
        # For now, we just test that the structure works
        
        self.assertIsNotNone(agent.planner)
        self.assertIsNotNone(agent.executor)
        self.assertIsNotNone(agent.synthesizer)


if __name__ == '__main__':
    unittest.main()

