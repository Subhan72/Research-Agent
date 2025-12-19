"""Calculator tool for safe mathematical operations."""
from typing import Dict, Any
import re
import math
import operator


class CalculatorTool:
    """Tool for performing mathematical calculations safely."""
    
    # Allowed operations
    ALLOWED_OPERATORS = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '**': operator.pow,
        '^': operator.pow,
        '%': operator.mod,
        '//': operator.floordiv
    }
    
    # Allowed functions
    ALLOWED_FUNCTIONS = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'log10': math.log10,
        'exp': math.exp,
        'pow': pow,
        'ceil': math.ceil,
        'floor': math.floor
    }
    
    def calculate(self, expression: str) -> Dict[str, Any]:
        """Safely evaluate a mathematical expression.
        
        Args:
            expression: Mathematical expression string
            
        Returns:
            Dictionary with:
            - expression: Original expression
            - result: Calculated result
            - success: Whether calculation succeeded
        """
        try:
            # Clean expression
            expression = expression.strip()
            
            # Remove common words
            expression = re.sub(r'\b(calculate|compute|what is|equals?)\b', '', expression, flags=re.IGNORECASE)
            expression = expression.strip('=')
            expression = expression.strip()
            
            # Validate expression contains only safe characters
            safe_pattern = r'^[0-9+\-*/().\s^%a-z_(),]+$'
            if not re.match(safe_pattern, expression, re.IGNORECASE):
                return {
                    'expression': expression,
                    'result': None,
                    'success': False,
                    'error': 'Expression contains invalid characters'
                }
            
            # Replace function names with safe versions
            for func_name, func in self.ALLOWED_FUNCTIONS.items():
                pattern = rf'\b{func_name}\s*\('
                expression = re.sub(pattern, f'__{func_name}(', expression, flags=re.IGNORECASE)
            
            # Replace ^ with ** for exponentiation
            expression = expression.replace('^', '**')
            
            # Create safe namespace
            safe_dict = {
                '__builtins__': {},
                'math': math,
                **{f'__{k}': v for k, v in self.ALLOWED_FUNCTIONS.items()}
            }
            
            # Evaluate expression
            result = eval(expression, safe_dict)
            
            # Handle infinity and NaN
            if not isinstance(result, (int, float)) or math.isnan(result) or math.isinf(result):
                return {
                    'expression': expression,
                    'result': None,
                    'success': False,
                    'error': 'Result is not a valid number'
                }
            
            return {
                'expression': expression,
                'result': float(result) if isinstance(result, (int, float)) else result,
                'success': True
            }
            
        except ZeroDivisionError:
            return {
                'expression': expression,
                'result': None,
                'success': False,
                'error': 'Division by zero'
            }
        except Exception as e:
            return {
                'expression': expression,
                'result': None,
                'success': False,
                'error': f'Calculation error: {str(e)}'
            }

