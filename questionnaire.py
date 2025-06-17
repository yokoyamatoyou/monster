"""Utilities for generating and scoring the questionnaire."""

from __future__ import annotations

import json
import random
from typing import Dict, List

import plotly.graph_objects as go

import prompts

AXES = [
    "特権意識と期待",
    "情動の不安定性",
    "不信感と猜疑心",
    "依存性と操作性",
    "統制欲求と完璧主義",
]


def generate_questionnaire(num_questions_per_axis: int = 5) -> List[dict]:
    """Generate a list of questions covering all axes."""
    questions: List[dict] = []
    for axis in AXES:
        for i in range(num_questions_per_axis):
            temp = 0.4 + 0.02 * i
            category = random.choice(prompts.AXIS_CATEGORIES.get(axis, ["一般"]))
            q_json = prompts.generate_question(axis, category=category, temperature=temp)
            try:
                q = json.loads(q_json)
            except json.JSONDecodeError:
                q = {"question_text": q_json, "axis": axis}
            questions.append(q)
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
