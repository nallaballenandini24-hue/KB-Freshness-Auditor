AI Usage Note
What AI Helped With
Generating the FastAPI backend code, database models, and API endpoints
Writing the freshness scoring logic (based on article age and ticket count)
Writing the prompt used to generate AI recommendations for stale articles
Debugging Python dependency and version compatibility errors during setup
Writing pytest test cases for the happy path
Helping prepare project documentation (README, prompts.md, this file)
Helping plan and structure the demo presentation
What AI Got Wrong
AI assistants initially suggested package versions (pydantic, sqlalchemy, psycopg2-binary) that were incompatible with Python 3.14, causing build errors. We had to identify the correct/updated versions manually.
Some initial folder creation commands needed correction due to shell-specific syntax differences (Windows PowerShell vs Linux bash).
The psycopg2-binary package was unnecessary since the project uses SQLite, but was initially included in requirements — AI helped identify this could be removed.
Best Prompts Used
The structured AI recommendation prompt (see prompts.md) — asking the AI to identify missing information, suggest updates, and provide a rewritten draft in a fixed format made the output easy to display in our dashboard.
Providing real context (article age, ticket complaints) instead of asking the AI to "just improve this article" — this produced much more specific and useful suggestions.
Step-by-step debugging prompts when fixing errors — describing the exact error message and asking "what does this mean and how do I fix it" helped resolve issues quickly.
Assumptions and Limitations
AI-generated content is a draft/suggestion only and requires human review before publishing to a real knowledge base.
AI assistance was used throughout development, but all code was reviewed and tested by team members before integratio
