from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.webhook import router as webhook_router
from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.mcp.github_client import GitHubMCPClient

settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    mcp_client = GitHubMCPClient(
        settings.github_mcp_token,
        settings.github_mcp_tool_set,
        settings.review_timeout_seconds,
        settings.github_mcp_command,
        settings.github_mcp_arg_list,
    )
    await mcp_client.connect()
    app.state.github_mcp_client = mcp_client
    try:
        yield
    finally:
        if mcp_client is not None:
            await mcp_client.close()


app = FastAPI(title="AI Code Review Agent", version="1.0.0", lifespan=lifespan)
app.include_router(webhook_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ai-code-review-agent"}
