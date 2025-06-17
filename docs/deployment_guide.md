# Deployment Guide

This document outlines how to set up and run the AI-driven patient profiling system in a production or staging environment.

## Requirements
- Python 3.11
- OpenAI API key
- Network access to reach the OpenAI API

## Setup Steps
1. Install the application dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set the `OPENAI_API_KEY` environment variable:
   ```bash
   export OPENAI_API_KEY=your-key-here
   ```
3. Launch the Streamlit app:
   ```bash
   streamlit run app.py
   ```
4. Run the automated tests whenever changes are made:
   ```bash
   pytest
   ```

## Data Storage
All questionnaire responses are stored in the `data/` directory as `interactions.csv`. Each entry includes a timestamp in UTC along with an anonymised evaluation summary. No personally identifying information is stored.

## Ethical Considerations
- The system is intended to enhance patient communication and should not be used to stigmatise or label patients.
- The consent message explaining anonymised data use must remain visible to participants before they begin the questionnaire.

