"""Utilities for generating and scoring the questionnaire."""

from __future__ import annotations

import json
import os
import random
from typing import Dict, List

import openai
import asyncio

import plotly.graph_objects as go

import prompts

AXES = [
    "特権意識と期待",
    "情動の不安定性",
    "不信感と猜疑心",
    "依存性と操作性",
    "統制欲求と完璧主義",
]


def _is_similar(text: str, existing: List[str]) -> bool:
    """Check similarity using GPT-4.1 mini rather than embeddings."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False
    client = openai.OpenAI(api_key=api_key)
    for t in existing:
        messages = [
            {
                "role": "system",
                "content": "次の二つの質問がほぼ同じ内容か判定し、似ていれば'はい'、違えば'いいえ'のみを返してください。",
            },
            {"role": "user", "content": f"Q1: {text}\nQ2: {t}"},
        ]
        try:
            resp = client.chat.completions.create(model=prompts.MODEL, messages=messages, temperature=0)
            ans = resp.choices[0].message.content.strip()
            if ans.startswith("はい") or ans.lower().startswith("yes"):
                return True
        except openai.OpenAIError:
            return False
    return False


async def _is_similar_async(text: str, existing: List[str]) -> bool:
    """Asynchronously check similarity using GPT-4.1 mini."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False
    client = openai.AsyncOpenAI(api_key=api_key)
    for t in existing:
        messages = [
            {
                "role": "system",
                "content": "次の二つの質問がほぼ同じ内容か判定し、似ていれば'はい'、違えば'いいえ'のみを返してください。",
            },
            {"role": "user", "content": f"Q1: {text}\nQ2: {t}"},
        ]
        try:
            resp = await client.chat.completions.create(model=prompts.MODEL, messages=messages, temperature=0)
            ans = resp.choices[0].message.content.strip()
            if ans.startswith("はい") or ans.lower().startswith("yes"):
                return True
        except openai.OpenAIError:
            return False
    return False


def _generate_unique_question(axis: str, existing: List[str], temp: float, category: str) -> dict:
    """Generate a question avoiding semantic similarity.

    The OpenAI API may occasionally return non-dictionary JSON such as a list or
    a plain string.  To ensure robustness we normalise the parsed value to a
    dictionary with ``question_text`` and ``axis`` keys before checking for
    similarity.
    """

    for _ in range(5):
        q_json = prompts.generate_question(axis, category=category, temperature=temp)
        try:
            parsed = json.loads(q_json)
        except json.JSONDecodeError:
            parsed = q_json

        # Normalise to a dict with required keys
        if isinstance(parsed, dict):
            question_text = parsed.get("question_text", "")
            axis_val = parsed.get("axis", axis)
        elif isinstance(parsed, list):
            if parsed:
                item = parsed[0]
                if isinstance(item, dict):
                    question_text = item.get("question_text", "")
                    axis_val = item.get("axis", axis)
                else:
                    question_text = str(item)
                    axis_val = axis
            else:
                question_text = ""
                axis_val = axis
        else:
            question_text = str(parsed)
            axis_val = axis

        q = {"question_text": question_text, "axis": axis_val}

        if not _is_similar(q["question_text"], existing):
            return q

    return q


async def _generate_unique_question_async(axis: str, existing: List[str], temp: float, category: str) -> dict:
    """Asynchronously generate a question avoiding semantic similarity."""
    for _ in range(5):
        q_json = await prompts.generate_question_async(axis, category=category, temperature=temp)
        try:
            parsed = json.loads(q_json)
        except json.JSONDecodeError:
            parsed = q_json

        if isinstance(parsed, dict):
            question_text = parsed.get("question_text", "")
            axis_val = parsed.get("axis", axis)
        elif isinstance(parsed, list):
            if parsed:
                item = parsed[0]
                if isinstance(item, dict):
                    question_text = item.get("question_text", "")
                    axis_val = item.get("axis", axis)
                else:
                    question_text = str(item)
                    axis_val = axis
            else:
                question_text = ""
                axis_val = axis
        else:
            question_text = str(parsed)
            axis_val = axis

        q = {"question_text": question_text, "axis": axis_val}

        if not await _is_similar_async(q["question_text"], existing):
            return q

    return q


import asyncio


async def _generate_axis_questions_async(
    axis: str,
    num_questions: int,
    existing: List[str],
    lock: asyncio.Lock,
) -> List[dict]:
    """Generate questions for a single axis asynchronously."""
    axis_questions: List[dict] = []
    for i in range(num_questions):
        temp = 0.4 + 0.02 * i
        category = random.choice(prompts.AXIS_CATEGORIES.get(axis, ["一般"]))
        q = await _generate_unique_question_async(axis, existing, temp, category)
        async with lock:
            existing.append(q["question_text"])
        axis_questions.append(q)
    return axis_questions


async def generate_questionnaire_async(num_questions_per_axis: int = 3) -> List[dict]:
    """Asynchronously generate questions for all axes."""
    questions: List[dict] = []
    existing_texts: List[str] = []
    lock = asyncio.Lock()

    tasks = [
        _generate_axis_questions_async(axis, num_questions_per_axis, existing_texts, lock)
        for axis in AXES
    ]
    results = await asyncio.gather(*tasks)
    for qs in results:
        questions.extend(qs)

    return questions


def generate_questionnaire(num_questions_per_axis: int = 3) -> List[dict]:
    """Synchronous wrapper around asynchronous questionnaire generation."""
    return asyncio.run(generate_questionnaire_async(num_questions_per_axis))


def score_answers(responses: List[dict]) -> Dict[str, float]:
    """Return average score per axis from a list of responses."""
    scores: Dict[str, List[int]] = {axis: [] for axis in AXES}
    for r in responses:
        axis = r["axis"]
        score = int(r["score"])
        if axis in scores:
            scores[axis].append(score)
    averages: Dict[str, float] = {}
    for axis, vals in scores.items():
        if vals:
            averages[axis] = sum(vals) / len(vals)
        else:
            averages[axis] = 0.0
    return averages


def radar_chart(scores: Dict[str, float]) -> go.Figure:
    """Create a radar chart from axis scores."""
    categories = list(scores.keys())
    values = list(scores.values())
    values.append(values[0])
    categories.append(categories[0])
    fig = go.Figure(
        data=[go.Scatterpolar(r=values, theta=categories, fill="toself")]
    )
    fig.update_layout(polar=dict(radialaxis=dict(range=[1, 5])), showlegend=False)
    return fig
