"""Prompt templates for the AI-driven patient profiling system."""
from __future__ import annotations

import os
from typing import List
import openai


def _call_openai(messages: List[dict], temperature: float) -> str:
    """Helper to call OpenAI chat completion."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-4.1", messages=messages, temperature=temperature
    )
    return response.choices[0].message["content"].strip()


def generate_question(axis: str, temperature: float = 0.4) -> str:
    """Generate a single question for the given axis."""
    system = (
        "You are a medical survey designer. Use non-clinical wording to inquire about "
        "patient personality traits. Format your reply as JSON with keys 'question_text' "
        "and 'axis'."
    )
    user = (
        "Generate one short question related to the following axis "
        f"'{axis}'."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return _call_openai(messages, temperature)


def feedback_for_patient(summary: str, temperature: float = 0.1) -> str:
    """Generate patient-facing feedback based on answer summary."""
    system = (
        "You are an empathetic counselor. Provide reassuring feedback summarizing what "
        "the patient values, avoiding mention of risk." 
    )
    user = (
        "Based on the following summary of questionnaire answers, write concise "
        "feedback titled '診療方針に関するご確認'.\n" + summary
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return _call_openai(messages, temperature)


def feedback_for_staff(summary: str, temperature: float = 0.1) -> str:
    """Generate staff-facing feedback in structured JSON."""
    system = (
        "You are an experienced clinical psychologist and risk manager."
    )
    user = (
        "Using the following score summary, produce analysis in JSON with keys "
        "'risk_profile_summary', 'caution_points', 'recommended_actions', "
        "'escalation_plan'.\n" + summary
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return _call_openai(messages, temperature)


def evaluation_summary(scores: dict, temperature: float = 0.1) -> str:
    """Summarize score rationale in ~200 characters."""
    system = "You summarize patient questionnaire results in around 200 Japanese characters."
    user = "Summarize the following scores: " + str(scores)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return _call_openai(messages, temperature)
