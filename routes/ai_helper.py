"""
AI helper module — wraps DeepSeek API (OpenAI-compatible) calls.
Reads API settings from the database automatically.
"""
import json
import requests
from models import db, AISettings


SYSTEM_PROMPT_TUTOR = """You are a professional English learning assistant (英语学习助手). Your role:
- Answer questions about English vocabulary, grammar, usage, and learning methods
- Always provide Chinese explanations with English examples
- When explaining a word, include: pronunciation, Chinese meaning, usage examples, and memory tips
- Be encouraging and friendly
- Keep responses concise but thorough
- If the user asks about translation, provide natural Chinese translations with explanations of key vocabulary and grammar points

You are helping a Chinese-speaking user learn English. Always respond in Chinese with English examples where helpful."""

SYSTEM_PROMPT_GRADER = """You are an English-Chinese translation grader. Your task:
1. Compare the user's Chinese translation against the original English text
2. Score the translation from 0-100 based on accuracy, fluency, and completeness
3. Identify specific errors and mark them

You MUST respond with ONLY valid JSON in this exact format (no markdown, no extra text):
{
  "score": 85,
  "overall": "Overall assessment in Chinese, 1-2 sentences",
  "errors": [
    {"original": "incorrect phrase in user's translation", "corrected": "correct Chinese translation", "explanation": "explanation in Chinese"}
  ],
  "corrected_version": "The full corrected Chinese translation"
}

If there are no errors, return an empty errors array and score 100."""


def get_ai_settings():
    """Get the AI settings from database. Returns (api_key, base_url, model)."""
    settings = AISettings.query.first()
    if not settings:
        return "", "https://api.deepseek.com", "deepseek-chat"
    return settings.api_key, settings.api_base_url, settings.model_name


def call_ai(messages, system_prompt=None, temperature=0.7, max_tokens=2000, timeout=60):
    """
    Call the AI API with given messages.
    Returns the AI response text, or raises an exception on error.
    """
    api_key, base_url, model = get_ai_settings()

    if not api_key:
        raise ValueError("请先在设置页面配置 AI API Key")

    import re
    base = base_url.rstrip('/')
    if re.search(r'/v\d+$', base):
        url = base + '/chat/completions'
    else:
        url = base + '/v1/chat/completions'

    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    payload = {
        "model": model,
        "messages": full_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=timeout)

    if resp.status_code != 200:
        try:
            err = resp.json()
            msg = err.get("error", {}).get("message", resp.text)
        except Exception:
            msg = resp.text
        raise RuntimeError(f"AI API 错误 (HTTP {resp.status_code}): {msg[:500]}")

    data = resp.json()
    return data["choices"][0]["message"]["content"]
