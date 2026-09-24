import shlex
from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_base_url: str = "https://openai.generative.engine.capgemini.com/v1"
    gep_api_key: str = ""
    model_name: str = "openai.gpt-5-mini"
    github_token: str = ""
    github_owner: str = ""
    github_webhook_secret: str = ""
    allowed_repositories: str = "*"
    allow_draft_reviews: bool = False
    scm_provider: str = "mcp"
    github_mcp_url: str = "https://api.githubcopilot.com/mcp/"
    github_mcp_token: str = ""
    github_mcp_transport: str = "stdio"
    github_mcp_command: str = "npx"
    github_mcp_args: str = "-y @modelcontextprotocol/server-github"
    github_mcp_tools: str = "get_pull_request_files,create_pull_request_review"
    github_rest_fallback: bool = False
    max_files: int = Field(default=40, ge=1)
    max_file_diff_chars: int = Field(default=12000, ge=1000)
    max_review_input_chars: int = Field(default=100000, ge=10000)
    review_timeout_seconds: float = Field(default=60, gt=0)
    mock_external_services: bool = True
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    @property
    def allowed_repository_set(self) -> set[str]:
        return {item.strip().lower() for item in self.allowed_repositories.split(",") if item.strip()}

    def repository_allowed(self, full_name: str) -> bool:
        allowed = self.allowed_repository_set
        return "*" in allowed or full_name.lower() in allowed or full_name.rsplit("/", 1)[-1].lower() in allowed

    @property
    def policy_path(self) -> Path:
        return Path(__file__).parents[1] / "rules" / "enterprise_review.md"

    @property
    def github_mcp_tool_set(self) -> set[str]:
        return {item.strip() for item in self.github_mcp_tools.split(",") if item.strip()}

    @property
    def github_mcp_arg_list(self) -> list[str]:
        return shlex.split(self.github_mcp_args)


@lru_cache
def get_settings() -> Settings:
    return Settings()
