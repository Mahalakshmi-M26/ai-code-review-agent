# Windows Setup Guide

## Prerequisites

Install Python 3.11+, Node.js with `npx`, GitHub access for the target repositories, and ngrok for local webhook exposure.

## Install

```powershell
cd "C:\path\to\AI_Code_Review_Agent"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with the Generative Engine key, webhook secret, MCP token, and repository policy. Do not commit `.env`.

## Configure the Local MCP Server

The default configuration starts:

```text
npx -y @modelcontextprotocol/server-github
```

The application passes `GITHUB_MCP_TOKEN` to that process as `GITHUB_PERSONAL_ACCESS_TOKEN` and requires the tools listed in `GITHUB_MCP_TOOLS`.

## Start FastAPI

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8000
```

Startup is successful only after MCP connects and required tools are discovered.

## Start ngrok

Open a second PowerShell window:

```powershell
ngrok http 8000
```

Copy the HTTPS forwarding URL.

## Configure GitHub

Create a repository webhook with:

- URL: `<ngrok-https-url>/webhooks/github`
- Content type: `application/json`
- Secret: the value of `GITHUB_WEBHOOK_SECRET`
- Event: `Pull requests`

## Test

Open or update a pull request in an allowed repository. Watch the FastAPI logs for MCP calls, the Generative Engine response, and `review_finished ... result=posted`. Then inspect the PR comment.

## Local Test Mode

Set `MOCK_EXTERNAL_SERVICES=true` to exercise the application without a real Generative Engine call. Unit tests always mock external services and never require GitHub credentials.

## Stop

Press `Ctrl+C` in the Uvicorn and ngrok terminals, then run `deactivate` if the virtual environment is active.
