"""Prompt templates for the AI-driven patient profiling system."""
from __future__ import annotations

import os
import random
from typing import List
import openai

# Predefined categories for each axis to diversify questions
AXIS_CATEGORIES = {
    "特権意識と期待": ["治療計画", "予約や待ち時間", "サービスへの要望"],
    "情動の不安定性": ["ストレス対処", "気分の変化", "不安への向き合い方"],
    "不信感と猜疑心": ["情報の透明性", "他院との比較", "説明への納得感"],
    "依存性と操作性": ["相談相手", "安心感を求める行動", "支援への期待"],
    "統制欲求と完璧主義": ["治療スケジュール管理", "生活リズム", "計画の厳密さ"],
}


def _call_openai(messages: List[dict], temperature: float) -> str:
    """Helper to call OpenAI chat completion."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")
    client = openai.OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4.1", messages=messages, temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        return f"APIError: {e}"


def generate_question(axis: str, category: str | None = None, temperature: float = 0.4) -> str:
    """Generate a single question for the given axis and optional category."""
    if category is None:
        category = random.choice(AXIS_CATEGORIES.get(axis, ["一般"]))
    system = (
        "You are a medical survey designer. Use non-clinical wording in Japanese to "
        "ask the patient about preferences or concerns as part of a treatment plan. "
        "The reply must be JSON with keys 'question_text' and 'axis'."
    )
    user = (
        f"Category: {category}. Generate one short question related to the axis '{axis}' "
        "that feels like part of routine consultation."
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
        "the patient values. Your tone must be supportive and avoid language that could "
        "stigmatize or label the patient. Mention nothing about risk."
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
        " Provide actionable suggestions in Japanese and avoid stigmatizing or"
        " labeling the patient."
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
