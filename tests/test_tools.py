"""Unit tests for tools."""
import unittest
from unittest.mock import Mock, patch, MagicMock
from backend.tools.calculator import CalculatorTool
from backend.tools.data_analysis import DataAnalysisTool
from backend.utils.validators import extract_numbers, validate_url, sanitize_url


class TestCalculatorTool(unittest.TestCase):
    """Test calculator tool."""
    
    def setUp(self):
        self.calculator = CalculatorTool()
    
    def test_simple_addition(self):
        result = self.calculator.calculate("2 + 2")
        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 4.0)
    
    def test_division(self):
        result = self.calculator.calculate("10 / 2")
        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 5.0)
    
    def test_division_by_zero(self):
        result = self.calculator.calculate("10 / 0")
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_complex_expression(self):
        result = self.calculator.calculate("(2 + 3) * 4")
        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 20.0)


class TestDataAnalysisTool(unittest.TestCase):
    """Test data analysis tool."""
    
    def setUp(self):
        self.analyzer = DataAnalysisTool()
    
    def test_extract_numbers(self):
        text = "The prices are $10, $20, and $30."
        result = self.analyzer.extract_data(text)
        self.assertGreater(result['count'], 0)
        self.assertIn('statistics', result)
    
    def test_create_table(self):
        data = [
            {'name': 'A', 'value': 10},
            {'name': 'B', 'value': 20}
        ]
        result = self.analyzer.create_table(data)
        self.assertEqual(result['rows'], 2)
        self.assertEqual(result['columns'], 2)


class TestValidators(unittest.TestCase):
    """Test validation utilities."""
    
    def test_extract_numbers(self):
        text = "There are 5 apples and 3 oranges."
        numbers = extract_numbers(text)
        self.assertIn(5.0, numbers)
        self.assertIn(3.0, numbers)
    
    def test_validate_url(self):
        self.assertTrue(validate_url("https://example.com"))
        self.assertTrue(validate_url("http://example.com"))
        self.assertFalse(validate_url("not-a-url"))
        self.assertFalse(validate_url("ftp://example.com"))
    
    def test_sanitize_url(self):
        url = sanitize_url("example.com")
        self.assertIsNotNone(url)
        self.assertTrue(url.startswith("http"))


if __name__ == '__main__':
    unittest.main()

