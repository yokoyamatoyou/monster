"""Prompt templates for the AI-driven patient profiling system."""
from __future__ import annotations

import os
import random
import asyncio
from typing import List, Optional
import openai

MODEL = "gpt-4.1-mini"

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
            model=MODEL, messages=messages, temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        return f"APIError: {e}"


async def _acall_openai(messages: List[dict], temperature: float) -> str:
    """Asynchronous helper to call OpenAI chat completion."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")
    client = openai.AsyncOpenAI(api_key=api_key)
    try:
        response = await client.chat.completions.create(
            model=MODEL, messages=messages, temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        return f"APIError: {e}"


def generate_question(axis: str, category: str | None = None, temperature: float = 0.4) -> str:
    """Generate a single question for the given axis and optional category."""
    if category is None:
        category = random.choice(AXIS_CATEGORIES.get(axis, ["一般"]))
    system = (
        "あなたは、臨床心理学とコミュニケーション設計の専門家です。"
        "あなたの任務は、患者の潜在的なコミュニケーションスタイルや価値観を**間接的に**把握するための質問を作成することです。"
        "この質問は、患者本人には『今後の治療方針を決めるための、ご自身の考えや好みをお伺いするアンケート』として提示されます。"
        "そのため、**絶対に、評価したり、診断したりするような印象を与えてはいけません。**"
        "質問を作成する際は、以下のルールを**厳格に**守ってください。\n\n"
        "### ルール:\n"
        "1. **間接的な表現:** 軸の名称（例：\"特権意識\"\u3000\"不信感\"）や、それに類する直接的な単語（例：\"特別扱い\"\u3000\"疑う\"）を絶対に使用しないでください。\n"
        "2. **言い換えの具体例:**\n"
        "   - **悪い例（直接的）:** \"特別な扱いを期待しますか？\"\n"
        "   - **良い例（間接的）:** \"治療計画を立てる上で、ご自身の意見や希望を積極的に伝えたいタイプですか？\" (これは『特権意識と期待』の軸を測るための質問です)\n"
        "   - **悪い例（直接的）:** \"医師の説明を疑うことがありますか？\"\n"
        "   - **良い例（間接的）:** \"治療について、複数の情報源からご自身で納得できるまで調べたいと感じますか？\" (これは『不信感と猜疑心』の軸を測るための質問です)\n"
        "3. **患者視点:** あくまで『診療方針への好み』を尋ねる自然な問いかけにしてください。SAPASやMSI-BPDの非臨床的な質問スタイルを参考にしてください。\n"
        "4. **出力形式:** 返信は必ず {'question_text': '（生成された質問文）', 'axis': '（対応する軸の名称）'} のJSON形式のみとし、他のテキストは一切含めないでください。"
    )
    user = (
        f"上記のルールを厳守し、軸 '{axis}', カテゴリ '{category}' に関連する質問を1つ生成してください。"
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return _call_openai(messages, temperature)


async def generate_question_async(
    axis: str, category: str | None = None, temperature: float = 0.4
) -> str:
    """Asynchronously generate a question."""
    if category is None:
        category = random.choice(AXIS_CATEGORIES.get(axis, ["一般"]))
    system = (
        "あなたは、臨床心理学とコミュニケーション設計の専門家です。"
        "あなたの任務は、患者の潜在的なコミュニケーションスタイルや価値観を**間接的に**把握するための質問を作成することです。"
        "この質問は、患者本人には『今後の治療方針を決めるための、ご自身の考えや好みをお伺いするアンケート』として提示されます。"
        "そのため、**絶対に、評価したり、診断したりするような印象を与えてはいけません。**"
        "質問を作成する際は、以下のルールを**厳格に**守ってください。\n\n"
        "### ルール:\n"
        "1. **間接的な表現:** 軸の名称（例：\"特権意識\"\u3000\"不信感\"）や、それに類する直接的な単語（例：\"特別扱い\"\u3000\"疑う\"）を絶対に使用しないでください。\n"
        "2. **言い換えの具体例:**\n"
        "   - **悪い例（直接的）:** \"特別な扱いを期待しますか？\"\n"
        "   - **良い例（間接的）:** \"治療計画を立てる上で、ご自身の意見や希望を積極的に伝えたいタイプですか？\" (これは『特権意識と期待』の軸を測るための質問です)\n"
        "   - **悪い例（直接的）:** \"医師の説明を疑うことがありますか？\"\n"
        "   - **良い例（間接的）:** \"治療について、複数の情報源からご自身で納得できるまで調べたいと感じますか？\" (これは『不信感と猜疑心』の軸を測るための質問です)\n"
        "3. **患者視点:** あくまで『診療方針への好み』を尋ねる自然な問いかけにしてください。SAPASやMSI-BPDの非臨床的な質問スタイルを参考にしてください。\n"
        "4. **出力形式:** 返信は必ず {'question_text': '（生成された質問文）', 'axis': '（対応する軸の名称）'} のJSON形式のみとし、他のテキストは一切含めないでください。"
    )
    user = (
        f"上記のルールを厳守し、軸 '{axis}', カテゴリ '{category}' に関連する質問を1つ生成してください。"
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return await _acall_openai(messages, temperature)




def feedback_for_patient(summary: str, user_name: Optional[str] = None, temperature: float = 0.1) -> str:
    """Generate patient-facing feedback based on answer summary."""
    system = (
        "あなたは共感的なカウンセラーです。SAPAS と MSI-BPD を参考にした質問への回答を踏まえ、"
        "患者が大切にしている価値観を要約し、安心感を与えるフィードバックを提供します。"
        "あなたのトーンは常に協力的で、患者を分類したり評価したりする言葉を完全に避けてください。"
        "否定的な名詞や評価的表現を使わず、安心感を与える前向きな言葉を選んでください。"
        "リスクについては一切言及してはいけません。ここでの主目的は、患者が『自分の気持ちを理解してもらえた』と感じることです。"
        "フィードバックは、回答内容を反映した個別のアドバイスとして、今後の治療計画に活かすための前向きなものとして構成してください。"
        "心理的な分析や診断と受け取られる可能性のある表現は、いかなる場合も使用しないでください。"
        "内容は日本語で300文字以上600文字未満にまとめてください。"
    )
    name_part = f"{user_name}さん" if user_name else "患者様"
    user = (
        f"{name_part}に向けて、以下の回答要約を参考に 診療方針に関するご確認 というタイトルでフィードバックを作成してください。"
        " 出力は300文字以上600文字未満の日本語にしてください。\n" + summary
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return _call_openai(messages, temperature)


async def feedback_for_patient_async(summary: str, user_name: Optional[str] = None, temperature: float = 0.1) -> str:
    """Asynchronously generate patient feedback."""
    name_part = f"{user_name}さん" if user_name else "患者様"
    system = (
        "あなたは共感的なカウンセラーです。SAPAS と MSI-BPD を参考にした質問への回答を踏まえ、"
        "患者が大切にしている価値観を要約し、安心感を与えるフィードバックを提供します。"
        "あなたのトーンは常に協力的で、患者を分類したり評価したりする言葉を完全に避けてください。"
        "否定的な名詞や評価的表現を使わず、安心感を与える前向きな言葉を選んでください。"
        "リスクについては一切言及してはいけません。ここでの主目的は、患者が『自分の気持ちを理解してもらえた』と感じることです。"
        "フィードバックは、回答内容を反映した個別のアドバイスとして、今後の治療計画に活かすための前向きなものとして構成してください。"
        "心理的な分析や診断と受け取られる可能性のある表現は、いかなる場合も使用しないでください。"
        "内容は日本語で300文字以上600文字未満にまとめてください。"
    )
    user = (
        f"{name_part}に向けて、以下の回答要約を参考に 診療方針に関するご確認 というタイトルでフィードバックを作成してください。"
        " 出力は300文字以上600文字未満の日本語にしてください。\n" + summary
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return await _acall_openai(messages, temperature)


def feedback_for_staff(summary: str, temperature: float = 0.1) -> str:
    """Generate staff-facing feedback in structured JSON."""
    system = (
        "You are an experienced clinical psychologist and hospital risk assessment specialist."
        " The questionnaire items follow SAPAS and MSI-BPD as closely as possible."
        " Provide actionable suggestions in Japanese and avoid stigmatizing or"
        " labeling the patient."
        " 回答内容に基づいたパーソナライズされた助言を、各項目合計300文字以上600文字未満に収まるよう調整してください。"
    )
    user = (
        "以下のスコア概要を使用して、指定のJSON形式で分析レポートを生成してください。\n"
        "各キーには以下の内容を含めてください:\n"
        "- 'risk_profile_summary': スコア全体から読み取れる、患者のコミュニケーションにおける全体的な傾向の要約\n"
        "- 'caution_points': 患者との信頼関係を損なう可能性があるため、スタッフが避けるべき具体的な言動のリスト\n"
        "- 'recommended_actions': 信頼関係を構築するために推奨される、具体的な声かけや対応のリスト\n"
        "- 'escalation_plan': 万が一、問題行動が見られた場合に備えた段階的な対応計画\n\n"
        "出力は合計300文字以上600文字未満になるようにしてください。\n"
        "JSONオブジェクト以外の文字列は出力しないでください。\n"
        f"スコア概要: {summary}"
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return _call_openai(messages, temperature)


async def feedback_for_staff_async(summary: str, temperature: float = 0.1) -> str:
    """Asynchronously generate staff-facing feedback."""
    system = (
        "You are an experienced clinical psychologist and hospital risk assessment specialist."
        " The questionnaire items follow SAPAS and MSI-BPD as closely as possible."
        " Provide actionable suggestions in Japanese and avoid stigmatizing or"
        " labeling the patient."
        " 回答内容に基づいたパーソナライズされた助言を、各項目合計300文字以上600文字未満に収まるよう調整してください。"
    )
    user = (
        "以下のスコア概要を使用して、指定のJSON形式で分析レポートを生成してください。\n"
        "各キーには以下の内容を含めてください:\n"
        "- 'risk_profile_summary': スコア全体から読み取れる、患者のコミュニケーションにおける全体的な傾向の要約\n"
        "- 'caution_points': 患者との信頼関係を損なう可能性があるため、スタッフが避けるべき具体的な言動のリスト\n"
        "- 'recommended_actions': 信頼関係を構築するために推奨される、具体的な声かけや対応のリスト\n"
        "- 'escalation_plan': 万が一、問題行動が見られた場合に備えた段階的な対応計画\n\n"
        "出力は合計300文字以上600文字未満になるようにしてください。\n"
        "JSONオブジェクト以外の文字列は出力しないでください。\n"
        f"スコア概要: {summary}"
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return await _acall_openai(messages, temperature)


def evaluation_summary(scores: dict, temperature: float = 0.1) -> str:
    """Summarize score rationale in ~200 characters."""
    system = (
        "You summarize patient questionnaire results in around 200 Japanese characters."
        " The questions are based on SAPAS and MSI-BPD, mapped to five behavioral axes."
    )
    user = "Summarize the following scores: " + str(scores)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return _call_openai(messages, temperature)


async def evaluation_summary_async(scores: dict, temperature: float = 0.1) -> str:
    """Asynchronously summarize score rationale."""
    system = (
        "You summarize patient questionnaire results in around 200 Japanese characters."
        " The questions are based on SAPAS and MSI-BPD, mapped to five behavioral axes."
    )
    user = "Summarize the following scores: " + str(scores)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return await _acall_openai(messages, temperature)
