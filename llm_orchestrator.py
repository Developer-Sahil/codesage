"""
CodeSage Backend - LLM Orchestrator Module
AI-powered code analysis using Groq API.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

try:
    import aiohttp
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False
    print("Warning: aiohttp not available. Install with: pip install aiohttp")


@dataclass
class LLMAnalysisResult:
    """LLM analysis results."""
    file_path: str
    language: str
    ai_complexity_score: float
    ai_quality_score: float
    code_smells: List[str]
    improvement_suggestions: List[str]
    refactoring_recommendations: List[Dict[str, Any]]
    architecture_insights: List[str]
    security_concerns: List[str]
    performance_suggestions: List[str]
    best_practices_violations: List[str]
    estimated_technical_debt: str
    confidence_score: float
    
    def __post_init__(self):
        # Ensure all list fields are initialized
        for field_name in ['code_smells', 'improvement_suggestions', 'refactoring_recommendations',
                          'architecture_insights', 'security_concerns', 'performance_suggestions',
                          'best_practices_violations']:
            if not hasattr(self, field_name) or getattr(self, field_name) is None:
                setattr(self, field_name, [])


class GroqLLMOrchestrator:
    """LLM Orchestrator using Groq API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.1-8b-instant"):
        """Initialize the Groq LLM Orchestrator."""
        if not ASYNC_AVAILABLE:
            raise ImportError("aiohttp is required for AI features. Install with: pip install aiohttp")
        
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key required. Set GROQ_API_KEY environment variable.")
        
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        self.analysis_prompt = """
Analyze this {language} code and provide insights in JSON format:

```{language}
{code}
```

Return JSON with:
- complexity_score (0-10)
- quality_score (0-10)
- code_smells: list of issues
- improvement_suggestions: list of improvements
- security_concerns: list of security issues
- performance_suggestions: list of optimizations
- best_practices_violations: list of violations
- technical_debt: "Low"/"Medium"/"High"
"""
    
    async def analyze_code_with_llm(self, code: str, language: str, file_path: str) -> Optional[LLMAnalysisResult]:
        """Analyze code using LLM."""
        try:
            prompt = self.analysis_prompt.format(
                language=language,
                code=code[:3000]  # Limit for API
            )
            
            response = await self._call_groq_api(prompt)
            if not response:
                return None
            
            try:
                data = json.loads(response)
            except json.JSONDecodeError:
                # Fallback data
                data = {
                    "complexity_score": 5.0,
                    "quality_score": 6.0,
                    "code_smells": ["Unable to parse AI response"],
                    "improvement_suggestions": [response[:100] + "..."],
                    "security_concerns": [],
                    "performance_suggestions": [],
                    "best_practices_violations": [],
                    "technical_debt": "Medium"
                }
            
            return LLMAnalysisResult(
                file_path=file_path,
                language=language,
                ai_complexity_score=float(data.get("complexity_score", 5.0)),
                ai_quality_score=float(data.get("quality_score", 6.0)),
                code_smells=data.get("code_smells", []),
                improvement_suggestions=data.get("improvement_suggestions", []),
                refactoring_recommendations=[],
                architecture_insights=[],
                security_concerns=data.get("security_concerns", []),
                performance_suggestions=data.get("performance_suggestions", []),
                best_practices_violations=data.get("best_practices_violations", []),
                estimated_technical_debt=data.get("technical_debt", "Medium"),
                confidence_score=0.8
            )
            
        except Exception as e:
            print(f"Error analyzing code: {str(e)}")
            return None
    
    async def _call_groq_api(self, prompt: str, max_tokens: int = 1500) -> Optional[str]:
        """Make API call to Groq."""
        try:
            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": 0.1
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.base_url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"].strip()
                    else:
                        error_text = await response.text()
                        print(f"Groq API error {response.status}: {error_text}")
                        return None
                        
        except Exception as e:
            print(f"Error calling Groq API: {str(e)}")
            return None
    
    def analyze_files_batch(self, files_data: List[Tuple[str, str, str]]) -> Dict[str, LLMAnalysisResult]:
        """Analyze multiple files in batch."""
        if not ASYNC_AVAILABLE:
            print("Warning: Async functionality not available")
            return {}
        
        return asyncio.run(self._analyze_files_batch_async(files_data))
    
    async def _analyze_files_batch_async(self, files_data: List[Tuple[str, str, str]]) -> Dict[str, LLMAnalysisResult]:
        """Async batch analysis."""
        results = {}
        semaphore = asyncio.Semaphore(3)  # Limit concurrent requests
        
        async def analyze_single_file(file_data):
            file_path, code, language = file_data
            async with semaphore:
                result = await self.analyze_code_with_llm(code, language, file_path)
                if result:
                    results[file_path] = result
                await asyncio.sleep(0.5)  # Rate limiting
        
        tasks = [analyze_single_file(fd) for fd in files_data]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    def is_available(self) -> bool:
        """Check if orchestrator is available."""
        return ASYNC_AVAILABLE and self.api_key is not None
    
    def test_connection(self) -> bool:
        """Test connection to Groq API."""
        if not ASYNC_AVAILABLE:
            return False
        
        try:
            return asyncio.run(self._test_connection_async())
        except:
            return False
    
    async def _test_connection_async(self) -> bool:
        """Async connection test."""
        try:
            response = await self._call_groq_api("Test connection. Respond with 'OK'.", max_tokens=10)
            return response is not None
        except:
            return False