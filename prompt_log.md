# Prompt Log

## Initial Scaffold Prompt

User requested a clean, beginner-readable Flask + HTML/CSS/JavaScript project for a CMU 15-113 Company Financial Health Dashboard.

Key requirements:

- Serve homepage at `/`
- Add API route `/api/company/<ticker>`
- Return mock AAPL data for now
- Include search input, button, overview metric cards, and at least one Chart.js chart
- Keep the MVP focused
- Do not add AI explanation layer yet
- Do not add company comparison yet

Architecture:

```text
Browser -> Flask backend -> SEC API later -> Python calculations -> Flask JSON response -> JavaScript dashboard
```
