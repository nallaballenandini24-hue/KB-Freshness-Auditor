# Prompts Used in KB Freshness Auditor

## 1. Freshness Audit - AI Recommendation Prompt

Prompts Used in KB Freshness Auditor
AI Recommendation Prompt
This prompt is used to generate update suggestions for stale KB articles.
"You are a technical writer maintaining IT knowledge base articles. The article below has been flagged as STALE based on its age and number of related support tickets. Article title: [title]. Article content: [content]. Related ticket complaints: [ticket summaries]. Task: 1) Identify what information is missing or outdated. 2) Suggest specific updates needed. 3) Provide a complete rewritten draft of the article."
Why this prompt works
It gives the AI real context so it knows exactly what changed, instead of guessing. It also asks for a structured response so we can show Missing Info, Suggested Updates, and Updated Draft separately in the dashboard.
Model Used
Groq API (Mixtral 8x7b)
AI Coding Assistant Usage
We used AI coding assistants during development for generating FastAPI backend code, debugging Python dependency errors, and writing pytest test cases.
