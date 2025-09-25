
import logging
# Setup logging - use Django's logging configuration
logger = logging.getLogger(__name__)
from ..exceptions import LLMServiceError
from ..sketch_converter import config


class LLMClient:
    def __init__(self, api_key, base_url):
        self.client = self.start_llm_client(api_key, base_url)
        self.usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

    def start_llm_client(self, api_key, base_url): 
        from openai import OpenAI
        if not api_key or not base_url:
            logger.warning (LLMServiceError("LLM API key or base URL is not configured."))
            return None
        init_error = None
        for _ in range(3):
            try:
                client = OpenAI(
                    api_key=api_key,
                    base_url=base_url,
                )
                logger.info("LLM client initialized successfully.")
                return client
            except Exception as e:
                logger.error(f"Failed to initialize LLM client: {e}")
                init_error = e
        raise LLMServiceError(f"Failed to initialize LLM client: {init_error}", "LLM")
    
    def chat(self, model, messages, temperature = 0.1):
        last_error = None
        if not self.client:
            logger.warning (LLMServiceError("LLM client not initialized.", "LLM")) 
            return None
        for _ in range(3):
            try:
                response = self.client.chat.completions.create(
                    model = model,
                    messages=messages,
                    temperature=temperature,
                )
                if response.usage:
                    logger.info(f"Token usage: {response.usage.total_tokens} total tokens.")
                    usage = getattr(response, "usage", None)
                    self.usage["prompt_tokens"] += usage.prompt_tokens
                    self.usage["completion_tokens"] += usage.completion_tokens
                    self.usage["total_tokens"] += usage.total_tokens
                else:
                    logger.warning("No token usage found in response.")
                return response
            except Exception as e:
                logger.error(f"LLM API call failed: {e}")
                last_error = e
                self.client = self.start_llm_client ()
                continue
        raise LLMServiceError(f"LLM API call failed: {last_error}", "LLM")
                
