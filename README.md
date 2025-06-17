# Monster

This repository contains code and documentation for an AI-driven patient profiling and communication support system.

- The latest development plan is in [docs/project_plan_v3.md](docs/project_plan_v3.md).
- Additional contributor instructions are provided in [AGENTS.md](AGENTS.md).
- Phase 1 implementation guidance is documented in [docs/phase1_instructions.md](docs/phase1_instructions.md).
- Phase 2 introduced a basic questionnaire flow with scoring and radar chart visualization.
- Phase 3 adds a UI mode selector allowing patients to answer the questionnaire and staff to review stored results.
- Phase 4 introduces consent messaging, error handling and automated tests. A
  deployment guide is provided in [docs/deployment_guide.md](docs/deployment_guide.md).
- Participants see a consent notice explaining anonymous data use before starting the questionnaire.

## Setup

1. Install Python 3.11 and create a virtual environment.
2. Install required packages (the app expects Streamlit version 1.25 or later):

   ```bash
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key in the environment variable `OPENAI_API_KEY`.

4. Run tests using `pytest`:

   ```bash
   pytest
   ```

5. Launch the application locally:

   ```bash
   streamlit run app.py
   ```

   Windows users can run `run_app.bat` for convenience:

   ```bat
   run_app.bat
   ```

## Repository structure

- `app.py` – Streamlit app with patient and staff modes.
- `prompts.py` – functions that call OpenAI to generate questions and feedback.
- `questionnaire.py` – utilities to generate questions, score answers and create radar charts.
- `data_persistence.py` – helper to save questionnaire data as CSV under `data/`.
- `static/` – contains custom CSS (`style.css`) and favicon (`favicon.svg`).
- `data/` – storage directory for interaction logs (created automatically).
