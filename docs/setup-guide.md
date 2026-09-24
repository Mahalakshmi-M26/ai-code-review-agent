# Windows Setup Guide

1. Open PowerShell in the project folder.
2. Create and activate a virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

3. Copy `.env.example` to `.env`.
4. Add `GEP_API_KEY`, `GITHUB_TOKEN`, and `GITHUB_WEBHOOK_SECRET` to `.env`; never commit it.
5. Set `ALLOWED_REPOSITORIES=owner/repo` for production or `*` for a demo.
6. Confirm `.vscode/mcp.json` is visible to VS Code and sign in to the official GitHub MCP server if using Copilot Agent mode.
7. Start the app with `python -m uvicorn app.main:app --reload --port 8000`.
8. Run `ngrok http 8000`, then configure GitHub's webhook URL as `<ngrok-url>/webhooks/github`.
9. Select JSON and the Pull requests event, then create or update a test PR.
10. Watch PowerShell logs and inspect the posted summary.
11. Run `pytest -q`.
12. Stop Uvicorn with `Ctrl+C`, deactivate with `deactivate`.

For a local smoke test without GitHub or the model, keep `MOCK_EXTERNAL_SERVICES=true`; unit tests demonstrate signed requests without exposing credentials.
