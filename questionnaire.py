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
    """Generate a question avoiding semantic similarity."""
    for _ in range(5):
        q_json = prompts.generate_question(axis, category=category, temperature=temp)
        try:
            q = json.loads(q_json)
        except json.JSONDecodeError:
            q = {"question_text": q_json, "axis": axis}
        if not _is_similar(q["question_text"], existing):
            return q
    return q


def generate_questionnaire(num_questions_per_axis: int = 5) -> List[dict]:
    """Generate a list of questions covering all axes."""
    questions: List[dict] = []
    existing_texts: List[str] = []
    for axis in AXES:
        for i in range(num_questions_per_axis):
            temp = 0.4 + 0.02 * i
            category = random.choice(prompts.AXIS_CATEGORIES.get(axis, ["一般"]))
            q = _generate_unique_question(axis, existing_texts, temp, category)
            questions.append(q)
            existing_texts.append(q["question_text"])
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
