"""JSON API endpoints for AJAX interactions."""
import csv
import io
import json
from datetime import date, datetime, timedelta
from flask import Blueprint, request, jsonify, Response
from models import db, Word, WordBook, WordBookItem, LearningRecord, WrongAnswer, DailyCheckin, SimilarWordGroup, SimilarWordItem
from models import TranslationPassage, TranslationAttempt
from gtts import gTTS
import os
import requests

api_bp = Blueprint("api", __name__)


# ─── Audio ──────────────────────────────────────────────

@api_bp.route("/audio/<int:word_id>")
def get_audio(word_id):
    """Generate and serve audio for a word."""
    word = Word.query.get_or_404(word_id)

    audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "audio")
    audio_file = os.path.join(audio_dir, f"{word.id}.mp3")

    # Generate if not exists
    if not os.path.exists(audio_file):
        try:
            tts = gTTS(text=word.word, lang="en", slow=False)
            tts.save(audio_file)
            word.audio_path = f"/static/audio/{word.id}.mp3"
            db.session.commit()
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": True, "audio_url": word.audio_path})


# ─── Quick Actions ──────────────────────────────────────

@api_bp.route("/quick-stats")
def quick_stats():
    """Return quick stats for dashboard refresh."""
    today = date.today()
    due_count = LearningRecord.query.filter(
        LearningRecord.next_review <= today
    ).count()
    unreviewed_wrong = WrongAnswer.query.filter_by(reviewed=False).count()

    today_checkin = DailyCheckin.query.filter_by(checkin_date=today).first()
    reviewed_today = today_checkin.reviewed_count if today_checkin else 0

    # Streak
    streak = 0
    current = today
    while DailyCheckin.query.filter_by(checkin_date=current).first():
        streak += 1
        current = current - timedelta(days=1)

    return jsonify({
        "due_count": due_count,
        "unreviewed_wrong": unreviewed_wrong,
        "reviewed_today": reviewed_today,
        "streak": streak,
    })


@api_bp.route("/word-suggest")
def word_suggest():
    """Autocomplete for word search."""
    q = request.args.get("q", "").strip()
    if len(q) < 1:
        return jsonify([])

    words = Word.query.filter(
        Word.word.ilike(f"{q}%")
    ).limit(10).all()

    return jsonify([
        {"id": w.id, "word": w.word, "definition": w.definition[:50]}
        for w in words
    ])


# ─── Import / Export ────────────────────────────────────

@api_bp.route("/export-csv")
def export_csv():
    """Export all words as CSV."""
    book_id = request.args.get("book_id", type=int)

    if book_id:
        word_ids = set(
            item.word_id for item in WordBookItem.query.filter_by(wordbook_id=book_id).all()
        )
        words = Word.query.filter(Word.id.in_(word_ids)).order_by(Word.word).all()
    else:
        words = Word.query.order_by(Word.word).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["word", "phonetic", "definition", "example_sentence",
                      "example_translation", "part_of_speech", "tags"])

    for w in words:
        writer.writerow([w.word, w.phonetic, w.definition, w.example_sentence,
                         w.example_translation, w.part_of_speech, w.tags])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=words_export.csv"}
    )


@api_bp.route("/export-json")
def export_json():
    """Export all words as JSON (full backup)."""
    book_id = request.args.get("book_id", type=int)

    if book_id:
        word_ids = set(
            item.word_id for item in WordBookItem.query.filter_by(wordbook_id=book_id).all()
        )
        words = Word.query.filter(Word.id.in_(word_ids)).order_by(Word.word).all()
    else:
        words = Word.query.order_by(Word.word).all()

    data = {
        "exported_at": datetime.utcnow().isoformat(),
        "total_words": len(words),
        "words": [w.to_dict() for w in words],
    }

    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=words_export.json"}
    )


@api_bp.route("/import-csv", methods=["POST"])
def import_csv():
    """Import words from CSV."""
    file = request.files.get("file")
    book_id = request.form.get("book_id", type=int)

    if not file:
        return jsonify({"success": False, "message": "请上传文件"})

    try:
        content = file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
    except Exception as e:
        return jsonify({"success": False, "message": f"文件解析失败: {str(e)}"})

    added = 0
    skipped = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):
        word_text = row.get("word", "").strip()
        definition = row.get("definition", "").strip()

        if not word_text or not definition:
            errors.append(f"第{row_num}行: 缺少单词或释义")
            continue

        existing = Word.query.filter_by(word=word_text).first()
        if existing:
            skipped += 1
            word_obj = existing
        else:
            word_obj = Word(
                word=word_text,
                phonetic=row.get("phonetic", "").strip(),
                definition=definition,
                example_sentence=row.get("example_sentence", "").strip(),
                example_translation=row.get("example_translation", "").strip(),
                part_of_speech=row.get("part_of_speech", "").strip(),
                tags=row.get("tags", "").strip(),
            )
            db.session.add(word_obj)
            db.session.flush()
            added += 1

        # Add to book
        if book_id:
            existing_item = WordBookItem.query.filter_by(
                wordbook_id=book_id, word_id=word_obj.id
            ).first()
            if not existing_item:
                db.session.add(WordBookItem(wordbook_id=book_id, word_id=word_obj.id))

    db.session.commit()

    return jsonify({
        "success": True,
        "added": added,
        "skipped": skipped,
        "errors": errors,
    })


@api_bp.route("/import-json", methods=["POST"])
def import_json():
    """Import words from JSON."""
    file = request.files.get("file")
    book_id = request.form.get("book_id", type=int)

    if not file:
        return jsonify({"success": False, "message": "请上传文件"})

    try:
        content = file.read().decode("utf-8")
        data = json.loads(content)
    except Exception as e:
        return jsonify({"success": False, "message": f"文件解析失败: {str(e)}"})

    words_data = data.get("words", [])
    added = 0
    skipped = 0

    for wd in words_data:
        word_text = wd.get("word", "").strip()
        definition = wd.get("definition", "").strip()

        if not word_text or not definition:
            continue

        existing = Word.query.filter_by(word=word_text).first()
        if existing:
            skipped += 1
            word_obj = existing
        else:
            word_obj = Word(
                word=word_text,
                phonetic=wd.get("phonetic", ""),
                definition=definition,
                example_sentence=wd.get("example_sentence", ""),
                example_translation=wd.get("example_translation", ""),
                part_of_speech=wd.get("part_of_speech", ""),
                tags=wd.get("tags", ""),
            )
            db.session.add(word_obj)
            db.session.flush()
            added += 1

        if book_id:
            existing_item = WordBookItem.query.filter_by(
                wordbook_id=book_id, word_id=word_obj.id
            ).first()
            if not existing_item:
                db.session.add(WordBookItem(wordbook_id=book_id, word_id=word_obj.id))

    db.session.commit()

    return jsonify({
        "success": True,
        "added": added,
        "skipped": skipped,
    })


# ─── Learning data ──────────────────────────────────────

@api_bp.route("/word-learning-stats/<int:word_id>")
def word_learning_stats(word_id):
    """Get learning stats for a single word."""
    word = Word.query.get_or_404(word_id)
    record = LearningRecord.query.filter_by(word_id=word_id).first()
    wrongs = WrongAnswer.query.filter_by(word_id=word_id).order_by(
        WrongAnswer.last_wrong_at.desc()
    ).all()

    return jsonify({
        "word": word.word,
        "definition": word.definition,
        "learning": {
            "status": record.status if record else None,
            "ease_factor": record.ease_factor if record else None,
            "interval_days": record.interval_days if record else None,
            "repetitions": record.repetitions if record else None,
            "next_review": record.next_review.isoformat() if record and record.next_review else None,
            "total_reviews": record.total_reviews if record else 0,
            "accuracy": record.accuracy if record else 0,
        } if record else None,
        "wrong_answers": [
            {
                "quiz_type": w.quiz_type,
                "user_answer": w.user_answer,
                "wrong_count": w.wrong_count,
                "last_wrong_at": w.last_wrong_at.isoformat() if w.last_wrong_at else None,
                "reviewed": w.reviewed,
            }
            for w in wrongs
        ],
    })


# ─── Online Dictionary Lookup ──────────────────────────

DICT_API = "https://api.dictionaryapi.dev/api/v2/entries/en"


@api_bp.route("/lookup-online")
def lookup_online():
    """Look up a word using the free Dictionary API."""
    word = request.args.get("word", "").strip()
    if not word:
        return jsonify({"success": False, "message": "请输入单词"})

    try:
        resp = requests.get(f"{DICT_API}/{word}", timeout=10)
        if resp.status_code == 404:
            return jsonify({"success": False, "message": f"未找到单词 \"{word}\""})
        if resp.status_code != 200:
            return jsonify({"success": False, "message": f"词典服务暂时不可用 (HTTP {resp.status_code})"})

        data = resp.json()
        result = _parse_dict_response(data)

        # Collect texts to translate in parallel
        from concurrent.futures import ThreadPoolExecutor, as_completed

        # Translate the word itself (get multiple translations from matches)
        word_translations = _translate_word_multi(word)

        # Translate all definitions (max 3 per POS) in parallel
        def_texts = []
        for meaning in result["meanings"]:
            for def_item in meaning["definitions"][:3]:
                if def_item["definition"]:
                    def_texts.append(def_item["definition"])

        translations = {}
        if def_texts:
            with ThreadPoolExecutor(max_workers=6) as executor:
                futures = {executor.submit(_translate_text, t): t for t in def_texts}
                for future in as_completed(futures, timeout=10):
                    try:
                        original = futures[future]
                        translations[original] = future.result()
                    except Exception:
                        pass

        # Apply word translations
        result["word_translations"] = word_translations

        # Apply definition translations to ALL definitions
        for meaning in result["meanings"]:
            for def_item in meaning["definitions"][:3]:
                if def_item["definition"] in translations:
                    def_item["translation"] = translations[def_item["definition"]]

        result["success"] = True
        return jsonify(result)

    except requests.exceptions.Timeout:
        return jsonify({"success": False, "message": "请求超时，请检查网络"})
    except requests.exceptions.ConnectionError:
        return jsonify({"success": False, "message": "网络连接失败，请检查网络"})
    except Exception as e:
        return jsonify({"success": False, "message": f"查询出错: {str(e)}"})


def _parse_dict_response(data):
    """Parse the Dictionary API response into a structured format."""
    result = {
        "word": "",
        "phonetic": "",
        "phonetic_audio": "",
        "meanings": [],
    }

    if not data:
        return result

    entry = data[0]
    result["word"] = entry.get("word", "")

    # Phonetic
    for p in entry.get("phonetics", []):
        if p.get("text") and not result["phonetic"]:
            result["phonetic"] = p["text"]
        if p.get("audio") and not result["phonetic_audio"]:
            result["phonetic_audio"] = p["audio"]

    # Meanings
    for meaning in entry.get("meanings", []):
        pos = meaning.get("partOfSpeech", "")
        m_obj = {
            "part_of_speech": pos,
            "definitions": [],
        }

        for i, d in enumerate(meaning.get("definitions", [])[:3]):
            def_item = {
                "definition": d.get("definition", ""),
                "example": d.get("example", ""),
                "synonyms": d.get("synonyms", [])[:5],
                "antonyms": d.get("antonyms", [])[:5],
            }
            m_obj["definitions"].append(def_item)

        if m_obj["definitions"]:
            result["meanings"].append(m_obj)

    return result


@api_bp.route("/import-online-word", methods=["POST"])
def import_online_word():
    """Import a word from online lookup into local database."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "无数据"})

    word_text = data.get("word", "").strip()
    phonetic = data.get("phonetic", "").strip()
    definition = data.get("definition", "").strip()
    example = data.get("example", "").strip()
    part_of_speech = data.get("part_of_speech", "").strip()
    book_id = data.get("book_id")

    if not word_text or not definition:
        return jsonify({"success": False, "message": "单词和释义不能为空"})

    # Check duplicate
    existing = Word.query.filter_by(word=word_text).first()
    if existing:
        # Still add to book if specified
        if book_id:
            existing_item = WordBookItem.query.filter_by(
                wordbook_id=book_id, word_id=existing.id
            ).first()
            if not existing_item:
                db.session.add(WordBookItem(wordbook_id=book_id, word_id=existing.id))
                db.session.commit()
        return jsonify({
            "success": True,
            "duplicate": True,
            "message": f"单词 \"{word_text}\" 已存在",
            "word_id": existing.id,
        })

    word_obj = Word(
        word=word_text,
        phonetic=phonetic,
        definition=definition,
        example_sentence=example,
        part_of_speech=part_of_speech,
    )
    db.session.add(word_obj)
    db.session.flush()

    if book_id:
        db.session.add(WordBookItem(wordbook_id=book_id, word_id=word_obj.id))

    db.session.commit()

    return jsonify({
        "success": True,
        "duplicate": False,
        "message": f"单词 \"{word_text}\" 已添加",
        "word_id": word_obj.id,
    })


# ─── AI Chat ──────────────────────────────────────────

@api_bp.route("/ai-test", methods=["POST"])
def ai_test():
    """Test AI API connectivity with current settings. Returns detailed diagnostics."""
    data = request.get_json() or {}
    api_key = data.get("api_key", "").strip()
    base_url = data.get("api_base_url", "").strip()
    model = data.get("model_name", "").strip()

    # Use provided values or fall back to database
    if not api_key or not base_url:
        from routes.ai_helper import get_ai_settings
        db_key, db_url, db_model = get_ai_settings()
        if not api_key:
            api_key = db_key
        if not base_url:
            base_url = db_url
        if not model:
            model = db_model

    if not api_key:
        return jsonify({"success": False, "message": "请先填写 API Key", "stage": "validation"})

    if not base_url:
        return jsonify({"success": False, "message": "请先选择 AI 服务商或填写 API Base URL", "stage": "validation"})

    import re
    base = base_url.rstrip('/')
    if re.search(r'/v\d+$', base):
        url = base + '/chat/completions'
    else:
        url = base + '/v1/chat/completions'

    payload = {
        "model": model or "deepseek-chat",
        "messages": [
            {"role": "user", "content": "Hello! Reply with just: OK"}
        ],
        "max_tokens": 20,
        "temperature": 0,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    import time
    start = time.time()

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        elapsed = round((time.time() - start) * 1000)

        if resp.status_code == 200:
            data = resp.json()
            reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return jsonify({
                "success": True,
                "message": f"✅ 连接成功！模型响应正常",
                "stage": "done",
                "detail": {
                    "model": model,
                    "base_url": base_url,
                    "latency_ms": elapsed,
                    "reply_preview": reply[:100],
                    "status_code": 200,
                }
            })
        elif resp.status_code == 401 or resp.status_code == 403:
            return jsonify({
                "success": False,
                "message": "❌ 认证失败：API Key 无效或已过期",
                "stage": "auth",
                "detail": {"status_code": resp.status_code, "latency_ms": elapsed}
            })
        elif resp.status_code == 404:
            return jsonify({
                "success": False,
                "message": "❌ 接口不存在 (404)：请检查 API Base URL 是否正确",
                "stage": "url",
                "detail": {"status_code": 404, "latency_ms": elapsed, "url": url}
            })
        else:
            try:
                err_body = resp.json()
                err_msg = err_body.get("error", {}).get("message", resp.text[:300])
            except Exception:
                err_msg = resp.text[:300]
            return jsonify({
                "success": False,
                "message": f"❌ 请求失败 (HTTP {resp.status_code}): {err_msg}",
                "stage": "api_error",
                "detail": {"status_code": resp.status_code, "latency_ms": elapsed, "error": err_msg}
            })

    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "message": "❌ 连接超时 (15s)：请检查网络或 API Base URL 是否可访问",
            "stage": "timeout"
        })
    except requests.exceptions.ConnectionError as e:
        return jsonify({
            "success": False,
            "message": f"❌ 无法连接到服务器：请检查 API Base URL 是否正确\n详情: {str(e)[:200]}",
            "stage": "connection"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"❌ 未知错误: {str(e)[:300]}",
            "stage": "unknown"
        })


@api_bp.route("/chat", methods=["POST"])
def ai_chat():
    """AI chat endpoint — sends messages to DeepSeek and returns the response."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "请提供消息"})

    messages = data.get("messages", [])
    if not messages:
        return jsonify({"success": False, "message": "消息不能为空"})

    try:
        from routes.ai_helper import call_ai, SYSTEM_PROMPT_TUTOR
        reply = call_ai(messages, system_prompt=SYSTEM_PROMPT_TUTOR, temperature=0.8, max_tokens=2000)
        return jsonify({"success": True, "reply": reply})
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)})
    except RuntimeError as e:
        return jsonify({"success": False, "message": str(e)})
    except Exception as e:
        return jsonify({"success": False, "message": f"AI 调用失败: {str(e)}"})


# ─── Translation Grading ──────────────────────────────

@api_bp.route("/translation/grade", methods=["POST"])
def grade_translation():
    """Submit a translation for AI grading."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "请提供翻译数据"})

    passage_id = data.get("passage_id")
    user_translation = data.get("user_translation", "").strip()

    if not passage_id or not user_translation:
        return jsonify({"success": False, "message": "缺少必要参数"})

    passage = TranslationPassage.query.get(passage_id)
    if not passage:
        return jsonify({"success": False, "message": "文章不存在"})

    try:
        from routes.ai_helper import call_ai, SYSTEM_PROMPT_GRADER

        prompt = f"""Original English text:
---
{passage.content}
---

User's Chinese translation:
---
{user_translation}
---

Please grade this translation and return the JSON result."""

        reply = call_ai(
            [{"role": "user", "content": prompt}],
            system_prompt=SYSTEM_PROMPT_GRADER,
            temperature=0.3,
            max_tokens=3000,
            timeout=120,
        )

        # Parse AI response as JSON
        # Strip markdown code fences if present
        cleaned = reply.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

        feedback = json.loads(cleaned)
        score = int(feedback.get("score", 0))

        # Save attempt
        attempt = TranslationAttempt(
            passage_id=passage_id,
            user_translation=user_translation,
            ai_score=score,
            ai_feedback=json.dumps(feedback, ensure_ascii=False),
        )
        db.session.add(attempt)
        db.session.commit()

        return jsonify({
            "success": True,
            "score": score,
            "feedback": feedback,
            "attempt_id": attempt.id,
        })

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)})
    except RuntimeError as e:
        return jsonify({"success": False, "message": str(e)})
    except json.JSONDecodeError:
        return jsonify({
            "success": False,
            "message": "AI 返回格式异常，请重试",
            "raw_reply": reply[:500] if 'reply' in dir() else "",
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"评分失败: {str(e)}"})


# ─── Quick Word Lookup (combined local + online) ─────

@api_bp.route("/word-quick-lookup")
def word_quick_lookup():
    """Combined quick lookup: local DB words + online dictionary + translation."""
    q = request.args.get("q", "").strip()
    if len(q) < 1:
        return jsonify({"success": False, "message": "请输入单词"})

    result = {
        "success": True,
        "word": q,
        "local": [],
        "online": None,
    }

    # Local search
    words = Word.query.filter(
        Word.word.ilike(f"{q}%")
    ).limit(5).all()
    result["local"] = [w.to_dict() for w in words]

    return jsonify(result)
