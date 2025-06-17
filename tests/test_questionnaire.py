import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import questionnaire

def test_score_answers():
    responses = [
        {"axis": "特権意識と期待", "score": 3},
        {"axis": "特権意識と期待", "score": 5},
        {"axis": "情動の不安定性", "score": 2},
        {"axis": "情動の不安定性", "score": 4},
    ]
    scores = questionnaire.score_answers(responses)
    assert scores["特権意識と期待"] == 4
    assert scores["情動の不安定性"] == 3


def test_generate_questionnaire_count(monkeypatch):
    import prompts

    def dummy_gen(axis: str, category: str | None = None, temperature: float = 0.4) -> str:
        return '{"question_text": "dummy", "axis": "' + axis + '"}'

    monkeypatch.setattr(prompts, "generate_question", dummy_gen)
    monkeypatch.setattr(questionnaire, "_is_similar", lambda *args, **kwargs: False)
    qs = questionnaire.generate_questionnaire()
    assert len(qs) == 15
    axes = {q["axis"] for q in qs}
    assert axes == set(questionnaire.AXES)
