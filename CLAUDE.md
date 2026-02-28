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
User data is collected during onboarding and included in every AI response.

**Parent flow**: name → role → age → children → concern → chat

**Caregiver flow**: name → role → **persona** → age → children → concern → chat

| Step | Question | Stored As |
|------|----------|-----------|
| 1 | "How would you like me to address you?" | `name` |
| 2 | "What is your role?" | `role` + `role_title` |
| 3 | "Which best describes you?" (caregivers only) | `persona` |
| 4 | "How old are you?" | `age` |
| 5 | "Who is in your care, and how old are they?" | `children` |
| 6 | "What is your main concern today?" | `main_concern` |

The full profile is injected into the system prompt so Hayden can personalize responses (use their name, reference their children, remember their concern).

**Name usage**: Hayden always addresses the user by the name they provided in step 1. This is enforced in the system prompt.

### Caregiver Personas
Caregivers get an additional question to identify their specific type. Each persona gets tailored guidance:

| Persona | How Hayden Adapts |
|---------|------------------|
| Nanny/Au Pair | Professional language, respects their training and experience |
| Babysitter | Very simple and actionable, reassuring (may be younger/less experienced) |
| Grandparent | Honors their experience while gently sharing current guidelines |
| Aunt/Uncle | Balances respect for parents' wishes with practical help |
| Older Sibling | Simple steps, encouraging, calming (may feel scared or overwhelmed) |
| Daycare Worker | Efficiency tips, group management focus |
| Foster Parent | Trauma-informed, sensitive to system navigation and trust-building |
| Stepparent | Sensitive to blended family dynamics, earning trust, respecting boundaries |
| Godparent/Family Friend | Helps them honor parents' wishes, builds confidence |
| Other Relative | Considers household dynamics and daily involvement |

**Code location**: `app.py` lines 47-59 (persona guidance), 132-156 (detection)

### Curriculum Fallback
Hayden first tries to answer from the Hayden Childcare Certification curriculum. If the answer isn't available, it asks for permission before using broader knowledge:

> "Based on the Hayden Curriculum, I do not have this specific answer. Are you comfortable with me accessing the wider vetted medical, government and deeply researched findings?"

Only after user confirmation will Hayden access wider sources (medical, government, research).

**Code location**: `app.py` lines 54-61 (profile init), 83-106 (capture), 109-119 (injection)

### Role-Based Language Adaptation
The app adjusts its language complexity based on the user's role (detected during onboarding):

| Role | Detection Keywords | Language Level |
|------|-------------------|----------------|
| Parent | mother, father, mom, dad, parent | College-level vocabulary, technical terms, nuanced explanations |
| Caregiver | anyone else (grandparents, aunts, uncles, siblings, nannies, babysitters, etc.) | 10th-grade reading level, no jargon, practical advice |

**Note**: Caregiver is anyone who isn't a parent. This includes grandparents, aunts, uncles, siblings, nannies, babysitters, and any other non-parent caring for a child.

**Code location**: `app.py` lines 27-40 (prompts), 88-94 (detection), 121-125 (selection)

### UI Styling
- **User messages**: Green (#4CAF50) for visual distinction
- **Assistant messages**: White (default)
- **Background**: Black
- **Avatars**: Hidden
