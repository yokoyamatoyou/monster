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
