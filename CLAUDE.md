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

### Onboarding Profile
User data is collected during onboarding and included in every AI response:

| Step | Question | Stored As |
|------|----------|-----------|
| 1 | "How would you like me to address you?" | `name` |
| 2 | "What is your role?" | `role` + `role_title` |
| 3 | "How old are you?" | `age` |
| 4 | "Who is in your care, and how old are they?" | `children` |
| 5 | "What is your main concern today?" | `main_concern` |

The full profile is injected into the system prompt so Hayden can personalize responses (use their name, reference their children, remember their concern).

**Code location**: `app.py` lines 54-61 (profile init), 83-106 (capture), 109-119 (injection)

### Role-Based Language Adaptation
The app adjusts its language complexity based on the user's role (detected during onboarding):

| Role | Detection Keywords | Language Level |
|------|-------------------|----------------|
| Parent | mother, father, mom, dad, parent | College-level vocabulary, technical terms, nuanced explanations |
| Caregiver | anything else (nanny, babysitter, etc.) | 10th-grade reading level, no jargon, practical advice |

**Code location**: `app.py` lines 27-40 (prompts), 88-94 (detection), 121-125 (selection)

### UI Styling
- **User messages**: Green (#4CAF50) for visual distinction
- **Assistant messages**: White (default)
- **Background**: Black
- **Avatars**: Hidden
