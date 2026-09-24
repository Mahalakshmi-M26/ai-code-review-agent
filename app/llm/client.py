import json
import logging
import re
from typing import Any
import httpx
from app.models.review import ReviewResult

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, base_url: str, api_key: str, model: str, timeout: float = 60, mock: bool = True):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.mock = mock

    async def review(self, prompt: str) -> ReviewResult:
        if self.mock or not self.api_key:
            return ReviewResult(summary="Demo mode: no external model call was made.", categories_reviewed=["Security", "Architecture", "Testing"])
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": self.model, "temperature": 0, "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": "Return only valid JSON matching the requested review schema."}, {"role": "user", "content": prompt}]}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        content = data["choices"][0]["message"]["content"]
        return self.parse_result(content)

    @staticmethod
    def parse_result(content: str | dict[str, Any]) -> ReviewResult:
        if isinstance(content, dict):
            return ReviewResult.model_validate(content)
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.IGNORECASE)
        try:
            return ReviewResult.model_validate(json.loads(cleaned))
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            logger.warning("Malformed model response: %s", type(exc).__name__)
            raise ValueError("Model response was not valid review JSON") from exc
