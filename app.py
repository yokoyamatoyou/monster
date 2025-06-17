"""Streamlit application for questionnaire and staff dashboard (Phase 3)."""
import json
import pathlib

import streamlit as st
import pandas as pd

import data_persistence
import prompts
import questionnaire

CONSENT_MESSAGE = (
    "このアンケートの回答は匿名化され、分析目的で利用されます。"\
    "個人を特定する情報は保存されません。"
)


STATIC_DIR = pathlib.Path(__file__).parent / "static"

st.set_page_config(
    page_title="Patient Profiling", page_icon=str(STATIC_DIR / "favicon.svg")
)

# Load custom CSS
css_path = STATIC_DIR / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def init_state() -> None:
    if "questions" not in st.session_state:
        st.session_state.questions = questionnaire.generate_questionnaire()
    if "answers" not in st.session_state:
        st.session_state.answers = []
    if "index" not in st.session_state:
        st.session_state.index = 0


def show_consent() -> None:
    """Display consent message before starting the questionnaire."""
    st.info(CONSENT_MESSAGE)


def save_results(scores: dict) -> None:
    summary = prompts.evaluation_summary(scores)
    for i, q in enumerate(st.session_state.questions):
        ans = st.session_state.answers[i]
        data_persistence.save_interaction(
            user_id="demo_user",
            question_text=q["question_text"],
            answer_text=str(ans["score"]),
            total_question_count=len(st.session_state.questions),
            evaluation_summary=summary,
        )


def show_results(scores: dict) -> None:
    st.subheader("結果")
    fig = questionnaire.radar_chart(scores)
    st.plotly_chart(fig, use_container_width=True)
    st.write("### 患者向けフィードバック")
    st.write(prompts.feedback_for_patient(json.dumps(scores)))
    st.write("### 医療従事者向けフィードバック")
    st.json(json.loads(prompts.feedback_for_staff(json.dumps(scores))))


def questionnaire_flow() -> None:
    if st.session_state.index >= len(st.session_state.questions):
        scores = questionnaire.score_answers(st.session_state.answers)
        save_results(scores)
        show_results(scores)
        return

    q = st.session_state.questions[st.session_state.index]
    st.write(f"**{q['question_text']}**")
    choice = st.radio(
        "回答を選択してください", [1, 2, 3, 4, 5], key=f"q{st.session_state.index}"
    )
    if st.button("次へ"):
        st.session_state.answers.append({"axis": q["axis"], "score": choice})
        st.session_state.index += 1
        st.experimental_rerun()


def staff_dashboard() -> None:
    """Display stored questionnaire results for staff."""
    st.subheader("医療従事者向け分析")
    csv_path = data_persistence.CSV_PATH
    if not csv_path.exists():
        st.write("データがまだありません。")
        return
    df = pd.read_csv(csv_path)
    if df.empty:
        st.write("データがまだありません。")
        return
    sessions = df[["user_id", "evaluation_summary"]].drop_duplicates().reset_index(drop=True)
    selected = st.selectbox(
        "ユーザーを選択してください", sessions.index,
        format_func=lambda i: f"{sessions.loc[i, 'user_id']} ({i})"
    )
    user_id = sessions.loc[selected, "user_id"]
    st.write("### 評価サマリー")
    st.write(sessions.loc[selected, "evaluation_summary"])
    st.write("### 回答一覧")
    st.table(df[df["user_id"] == user_id][["question_text", "answer_text"]])


def main() -> None:
    st.title("Patient Profiling System")
    mode = st.sidebar.radio("モードを選択", ("患者モード", "医療従事者モード"))
    if mode == "患者モード":
        show_consent()
        init_state()
        questionnaire_flow()
    else:
        staff_dashboard()


if __name__ == "__main__":
    main()

