# Hayden App

## Overview
AI-powered childcare guidance app built with Streamlit and Claude API.

## Deployment
- **Hosting**: Streamlit Cloud (auto-deploys from GitHub)
- **Live URL**: https://hayden-childcare.streamlit.app
- **Repo**: git@github.com:HaydenCo2026/hayden-app.git

### To deploy
Push to `main` branch - Streamlit Cloud picks up changes automatically.

```bash
git add <files>
git commit -m "message"
git push
```

### Git authentication
Uses SSH key (`~/.ssh/id_ed25519`) - no tokens needed, won't expire.

## Secrets
API keys are stored in Streamlit Cloud dashboard (Settings > Secrets), not in the repo.
