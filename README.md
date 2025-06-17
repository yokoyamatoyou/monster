# Monster

This repository contains code and documentation for an AI-driven patient profiling and communication support system.

- The latest development plan is in [docs/project_plan_v3.md](docs/project_plan_v3.md).
- Additional contributor instructions are provided in [AGENTS.md](AGENTS.md).
- Phase 1 implementation guidance is documented in [docs/phase1_instructions.md](docs/phase1_instructions.md).
- Phase 2 introduces a basic questionnaire flow with scoring and radar chart visualization.

## Setup

1. Install Python 3.11 and create a virtual environment.
2. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key in the environment variable `OPENAI_API_KEY`.

## Repository structure (Phase 2)

- `app.py` – Streamlit app implementing the questionnaire flow.
- `prompts.py` – functions that call OpenAI to generate questions and feedback.
- `questionnaire.py` – utilities to generate questions, score answers and create radar charts.
- `data_persistence.py` – helper to save questionnaire data as CSV under `data/`.
- `static/` – contains custom CSS (`style.css`) and favicon (`favicon.svg`).
- `data/` – storage directory for interaction logs (created automatically).
