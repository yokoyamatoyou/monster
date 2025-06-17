# Monster

This repository contains code and documentation for an AI-driven patient profiling and communication support system.

- The latest development plan is in [docs/project_plan_v3.md](docs/project_plan_v3.md).
- Additional contributor instructions are provided in [AGENTS.md](AGENTS.md).
- Phase 1 implementation guidance is documented in [docs/phase1_instructions.md](docs/phase1_instructions.md).

## Setup

1. Install Python 3.11 and create a virtual environment.
2. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key in the environment variable `OPENAI_API_KEY`.

## Repository structure (Phase 1)

- `prompts.py` – functions that call OpenAI to generate questions and feedback.
- `data_persistence.py` – helper to save questionnaire data as CSV under `data/`.
- `static/` – contains custom CSS (`style.css`) and favicon (`favicon.svg`).
- `data/` – storage directory for interaction logs (created automatically).
