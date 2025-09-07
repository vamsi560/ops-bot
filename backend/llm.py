# LLM Integration for Gemini, Hugging Face, and other models
from fastapi import HTTPException
import requests
import json
from typing import Dict, Any, Optional

class LLMClient:
    def __init__(self, provider: str, api_key: str = None, model: str = None, endpoint: str = None):
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint
        
        # Set default endpoints based on provider
        if self.provider == "gemini" and not self.endpoint:
            self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models"
        elif self.provider == "huggingface" and not self.endpoint:
            self.endpoint = "https://api-inference.huggingface.co/models"
        elif self.provider == "openai" and not self.endpoint:
            self.endpoint = "https://api.openai.com/v1/chat/completions"

    def query(self, prompt: str, context: dict = None) -> str:
        """Query the LLM with the given prompt and context"""
        try:
            if self.provider == "gemini":
                return self._query_gemini(prompt, context)
            elif self.provider == "huggingface":
                return self._query_huggingface(prompt, context)
            elif self.provider == "openai":
                return self._query_openai(prompt, context)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported LLM provider: {self.provider}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM query failed: {str(e)}")

    def _query_gemini(self, prompt: str, context: dict = None) -> str:
        """Query Google Gemini API"""
        if not self.api_key:
            raise HTTPException(status_code=400, detail="Gemini API key is required")
        
        if not self.model:
            self.model = "gemini-1.5-flash"  # Default model
        
        # Prepare the prompt with context
        full_prompt = self._prepare_prompt_with_context(prompt, context)
        
        url = f"{self.endpoint}/{self.model}:generateContent"
        headers = {
            "Content-Type": "application/json",
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            }
        }
        
        # Add API key as query parameter
        params = {"key": self.api_key}
        
        response = requests.post(url, json=payload, headers=headers, params=params)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Gemini API error: {response.text}")
        
        result = response.json()
        
        if "candidates" in result and len(result["candidates"]) > 0:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            raise HTTPException(status_code=500, detail="No response from Gemini")

    def _query_huggingface(self, prompt: str, context: dict = None) -> str:
        """Query Hugging Face Inference API"""
        if not self.api_key:
            raise HTTPException(status_code=400, detail="Hugging Face API key is required")
        
        if not self.model:
            self.model = "microsoft/DialoGPT-large"  # Default model
        
        # Prepare the prompt with context
        full_prompt = self._prepare_prompt_with_context(prompt, context)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_length": 512,
                "temperature": 0.7,
                "do_sample": True
            }
        }
        
        url = f"{self.endpoint}/{self.model}"
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Hugging Face API error: {response.text}")
        
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            if "generated_text" in result[0]:
                return result[0]["generated_text"]
            elif "text" in result[0]:
                return result[0]["text"]
        
        # Fallback for different response formats
        return str(result)

    def _query_openai(self, prompt: str, context: dict = None) -> str:
        """Query OpenAI API"""
        if not self.api_key:
            raise HTTPException(status_code=400, detail="OpenAI API key is required")
        
        if not self.model:
            self.model = "gpt-3.5-turbo"  # Default model
        
        # Prepare the prompt with context
        full_prompt = self._prepare_prompt_with_context(prompt, context)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant helping with operations data analysis. Provide clear, helpful answers based on the provided context."
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        response = requests.post(self.endpoint, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {response.text}")
        
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            raise HTTPException(status_code=500, detail="No response from OpenAI")

    def _prepare_prompt_with_context(self, prompt: str, context: dict = None) -> str:
        """Prepare the prompt with context information"""
        if not context:
            return prompt
        
        context_str = ""
        
        # Add bot information
        if "bot_info" in context:
            bot_info = context["bot_info"]
            context_str += f"Bot: {bot_info.get('name', 'Operations Bot')}\n"
            context_str += f"Description: {bot_info.get('description', '')}\n"
            context_str += f"Available Categories: {', '.join(bot_info.get('categories', []))}\n\n"
        
        # Add data summary
        if "data_summary" in context:
            summary = context["data_summary"]
            context_str += f"Data Summary:\n"
            context_str += f"- Total Categories: {summary.get('total_categories', 0)}\n"
            context_str += f"- Total Files: {summary.get('total_files', 0)}\n"
            context_str += f"- Last Scan: {summary.get('last_scan', 'Unknown')}\n\n"
        
        # Add available data
        if "available_data" in context:
            available_data = context["available_data"]
            if available_data:
                context_str += "Available Data:\n"
                for category, data in available_data.items():
                    context_str += f"- {category}: {data.get('file_count', 0)} files\n"
                    if data.get('files'):
                        context_str += f"  Files: {', '.join(data['files'][:5])}"  # Show first 5 files
                        if len(data['files']) > 5:
                            context_str += f" (and {len(data['files']) - 5} more)"
                        context_str += "\n"
                context_str += "\n"
        
        # Combine context and prompt
        full_prompt = f"{context_str}Question: {prompt}\n\nPlease provide a helpful answer based on the available data."
        
        return full_prompt

    def get_available_models(self) -> Dict[str, list]:
        """Get available models for each provider"""
        return {
            "gemini": [
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-1.0-pro"
            ],
            "huggingface": [
                "microsoft/DialoGPT-large",
                "facebook/blenderbot-400M-distill",
                "microsoft/DialoGPT-medium",
                "google/flan-t5-large",
                "EleutherAI/gpt-neo-2.7B"
            ],
            "openai": [
                "gpt-3.5-turbo",
                "gpt-4",
                "gpt-4-turbo"
            ]
        }
