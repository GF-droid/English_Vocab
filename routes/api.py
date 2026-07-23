"""JSON API endpoints for AJAX interactions."""
import csv
import io
import json
from datetime import date, datetime, timedelta
from flask import Blueprint, request, jsonify, Response
from models import db, Word, WordBook, WordBookItem, LearningRecord, WrongAnswer, DailyCheckin, SimilarWordGroup, SimilarWordItem
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
