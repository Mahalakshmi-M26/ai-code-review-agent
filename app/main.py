from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.config import get_settings
from app.github_mcp import GitHubMCPClient
from app.webhook import router as webhook_router
import logging

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    mcp_client = GitHubMCPClient(
        settings.github_mcp_token,
        settings.github_mcp_tool_set,
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
