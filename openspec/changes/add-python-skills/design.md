# add-python-skills — Design

## Goal
Create five Python Claude Code skills under `~/.claude/skills/`, each as a standalone `SKILL.md` providing expert guidance for a specific domain used in the JR ticket automation project.

## Approach
Follow the exact same structure as existing Android skills: one folder per skill containing a single `SKILL.md` with YAML frontmatter (`name`, `description`) and expert guidance content. Each skill is scoped to one domain so Claude loads only the relevant knowledge when needed. Content is tailored to the JR Playwright ticket-snatching context.

## Key Decisions
- **One skill = one domain**: Keeps each SKILL.md focused; Claude invokes only what's relevant.
- **Playwright over Selenium**: `python-automation` targets `async_playwright` (async-first, faster, better DX).
- **Anthropic SDK (not LangChain)**: `python-llm-integration` uses the official `anthropic` Python SDK directly, matching the project's likely stack.
- **Simple mode**: No pytest fixtures or test scaffolding are written as part of this change; `python-testing` documents how the user should write tests going forward.

## File Structure
- `~/.claude/skills/python-automation/SKILL.md` — Playwright automation, retry logic, APScheduler, cookie sessions, anti-detection
- `~/.claude/skills/python-fastapi/SKILL.md` — FastAPI routes, Pydantic settings, BackgroundTasks, webhook notifications
- `~/.claude/skills/python-llm-integration/SKILL.md` — Anthropic SDK, tool use, Vision, streaming, cost control
- `~/.claude/skills/python-data-science/SKILL.md` — pandas/numpy best practices, ticket availability analysis, matplotlib, CSV/SQLite
- `~/.claude/skills/python-testing/SKILL.md` — pytest-asyncio, Playwright page.route() mocking, fixtures, parametrize

## Out of Scope
- Actual implementation of the JR ticket automation script
- LangChain, OpenAI, or other LLM provider integrations
- Docker / deployment configuration
- CI/CD pipeline setup
