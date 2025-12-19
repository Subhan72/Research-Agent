"""Text summarization tool using Groq LLM."""
from typing import Dict, Any, Optional
import config
from backend.utils.llm_client import GroqClient


class SummarizerTool:
    """Tool for summarizing text using LLM."""
    
    def __init__(self, llm_client: Optional[GroqClient] = None):
        """Initialize summarizer.
        
        Args:
            llm_client: Groq client instance. If None, creates new one
        """
        self.llm = llm_client or GroqClient()
    
    def summarize(
        self,
        text: str,
        max_length: Optional[int] = None,
        style: str = "concise"
    ) -> Dict[str, Any]:
        """Summarize text using LLM.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length in words. If None, uses 100
            style: Summary style ('concise', 'detailed', 'bullet')
            
        Returns:
            Dictionary with:
            - summary: Summarized text
            - original_length: Original text length
            - summary_length: Summary length
            - compression_ratio: Compression ratio
            - success: Whether summarization succeeded
        """
        if not text or len(text.strip()) < 10:
            return {
                'summary': text,
                'original_length': len(text),
                'summary_length': len(text),
                'compression_ratio': 1.0,
                'success': False,
                'error': 'Text too short to summarize'
            }
        
        max_length = max_length or 100
        
        # Truncate text if too long (to save tokens)
        max_input_length = 2000
        if len(text) > max_input_length:
            text = text[:max_input_length] + "..."
        
        # Create prompt based on style
        if style == "bullet":
            prompt = f"Summarize the following text in bullet points (maximum {max_length} words):\n\n{text}"
        elif style == "detailed":
            prompt = f"Provide a detailed summary of the following text (maximum {max_length} words):\n\n{text}"
        else:  # concise
            prompt = f"Provide a concise summary of the following text (maximum {max_length} words):\n\n{text}"
        
        system_prompt = "You are a helpful assistant that creates clear and accurate summaries."
        
        try:
            summary = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=min(max_length * 2, 500),  # Rough token estimate
                temperature=0.3  # Lower temperature for more consistent summaries
            )
            
            summary = summary.strip()
            
            return {
                'summary': summary,
                'original_length': len(text),
                'summary_length': len(summary),
                'compression_ratio': len(summary) / len(text) if text else 1.0,
                'success': True
            }
            
        except Exception as e:
            return {
                'summary': '',
                'original_length': len(text),
                'summary_length': 0,
                'compression_ratio': 0.0,
                'success': False,
                'error': str(e)
            }

