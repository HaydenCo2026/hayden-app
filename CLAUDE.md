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

## Features

### Role-Based Language Adaptation
The app adjusts its language complexity based on the user's role (detected during onboarding):

| Role | Detection Keywords | Language Level |
|------|-------------------|----------------|
| Parent | mother, father, mom, dad, parent | College-level vocabulary, technical terms, nuanced explanations |
| Caregiver | anything else (nanny, babysitter, etc.) | 10th-grade reading level, no jargon, practical advice |

**Code location**: `app.py` lines 26-39 (prompts), 75-80 (detection), 89-92 (selection)

### UI Styling
- **User messages**: Green (#4CAF50) for visual distinction
- **Assistant messages**: White (default)
- **Background**: Black
- **Avatars**: Hidden
