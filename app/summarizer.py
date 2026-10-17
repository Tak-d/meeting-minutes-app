from anthropic import Anthropic
from app.config import settings

client = Anthropic(api_key=settings.anthropic_api_key)

SYSTEM = """あなたは優秀な議事録作成アシスタントです。
提供された会議の文字起こしから、以下のフォーマットで議事録を作成してください。

# 会議議事録

## 日時
（抽出できなければ「不明」）

## 参加者
（抽出できなければ「不明」）

## 議題
（箇条書き）

## 決定事項
（箇条書き）

## アクションアイテム
- [ ] タスク（担当者）

ルール:
- 出力はMarkdown形式。
- 前置きや説明は不要。
- 発言のニュアンスを損なわない。
"""

def generate_minutes(transcript: str) -> str:
    msg = client.messages.create(
        model=settings.claude_model,
        max_tokens=settings.max_tokens,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"以下の文字起こしから議事録を作成してください。\n\n---\n{transcript}\n---"}],
    )
    return msg.content[0].text