"""Utilities for generating and scoring the questionnaire."""

from __future__ import annotations

import json
import os
import random
from typing import Dict, List

import openai

import plotly.graph_objects as go

import prompts

AXES = [
    "特権意識と期待",
    "情動の不安定性",
    "不信感と猜疑心",
    "依存性と操作性",
    "統制欲求と完璧主義",
]


def _embedding(text: str) -> List[float]:
    """Return embedding for text using OpenAI API; empty list if unavailable."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return []
    client = openai.OpenAI(api_key=api_key)
    try:
        resp = client.embeddings.create(model="text-embedding-3-small", input=[text])
        return resp.data[0].embedding
    except openai.OpenAIError:
        return []


def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2:
        return 0.0
    num = sum(a * b for a, b in zip(v1, v2))
    denom = (sum(a * a for a in v1) ** 0.5) * (sum(b * b for b in v2) ** 0.5)
    if denom == 0:
        return 0.0
    return num / denom


def _is_similar(text: str, existing: List[str], threshold: float = 0.9) -> bool:
    emb1 = _embedding(text)
    for t in existing:
        emb2 = _embedding(t)
        if _cosine_similarity(emb1, emb2) >= threshold:
            return True
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


from concurrent.futures import ThreadPoolExecutor
import threading


def _generate_axis_questions(
    axis: str,
    num_questions: int,
    existing: List[str],
    lock: threading.Lock,
) -> List[dict]:
    """Generate questions for a single axis in a thread."""
    axis_questions: List[dict] = []
    for i in range(num_questions):
        temp = 0.4 + 0.02 * i
        category = random.choice(prompts.AXIS_CATEGORIES.get(axis, ["一般"]))
        q = _generate_unique_question(axis, existing, temp, category)
        with lock:
            existing.append(q["question_text"])
        axis_questions.append(q)
    return axis_questions


def generate_questionnaire(num_questions_per_axis: int = 3) -> List[dict]:
    """Generate a list of questions covering all axes using threads."""
    questions: List[dict] = []
    existing_texts: List[str] = []
    lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=len(AXES)) as executor:
        futures = [
            executor.submit(
                _generate_axis_questions,
                axis,
                num_questions_per_axis,
                existing_texts,
                lock,
            )
            for axis in AXES
        ]
        for f in futures:
            questions.extend(f.result())

    return questions


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
