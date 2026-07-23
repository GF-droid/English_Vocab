import random
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from models import db, Word, WrongAnswer, LearningRecord, WordBookItem, SimilarWordGroup, SimilarWordItem

quiz_bp = Blueprint("quiz", __name__)


@quiz_bp.route("/")
def quiz_home():
    """Quiz mode selection page."""
    return render_template("quiz.html")


@quiz_bp.route("/mc")
def quiz_mc():
    """Multiple choice quiz."""
    book_id = request.args.get("book_id", type=int)
    count = request.args.get("count", 10, type=int)
    wrong_only = request.args.get("wrong_only", "0") == "1"
    similar_group_id = request.args.get("similar_group", type=int)

    # Select words for quiz
    if wrong_only:
        wrong_word_ids = set(
            wa.word_id for wa in WrongAnswer.query.filter_by(reviewed=False).all()
        )
        if not wrong_word_ids:
            flash("没有未复习的错题", "info")
            return redirect(url_for("quiz.quiz_home"))
        words = Word.query.filter(Word.id.in_(wrong_word_ids)).all()
    elif similar_group_id:
        word_ids = set(
            item.word_id for item in SimilarWordItem.query.filter_by(group_id=similar_group_id).all()
        )
        words = Word.query.filter(Word.id.in_(word_ids)).all()
    elif book_id:
        word_ids = set(
            item.word_id for item in WordBookItem.query.filter_by(wordbook_id=book_id).all()
        )
        words = Word.query.filter(Word.id.in_(word_ids)).all()
    else:
        words = Word.query.all()

    if len(words) < 4:
        flash("至少需要4个单词才能进行选择题测验", "warning")
        return redirect(url_for("quiz.quiz_home"))

    selected = random.sample(words, min(count, len(words)))

    # Build quiz data: for each word, generate 3 distractors
    quiz_words = []
    all_words = [w for w in words if w.id not in {s.id for s in selected}]

    for word in selected:
        # Get distractors of similar length or random
        distractors = random.sample(
            all_words, min(3, len(all_words))
        ) if len(all_words) >= 3 else random.sample(
            [w for w in Word.query.all() if w.id != word.id], min(3, len(Word.query.all()) - 1)
        )
        options = [word] + distractors
        random.shuffle(options)

        quiz_words.append({
            "word": word,
            "options": options,
        })

    return render_template("quiz_mc.html", quiz_words=quiz_words, total=len(quiz_words))


@quiz_bp.route("/spell")
def quiz_spell():
    """Spelling quiz."""
    book_id = request.args.get("book_id", type=int)
    count = request.args.get("count", 10, type=int)
    wrong_only = request.args.get("wrong_only", "0") == "1"

    if wrong_only:
        wrong_word_ids = set(
            wa.word_id for wa in WrongAnswer.query.filter_by(reviewed=False).all()
        )
        if not wrong_word_ids:
            flash("没有未复习的错题", "info")
            return redirect(url_for("quiz.quiz_home"))
        words = Word.query.filter(Word.id.in_(wrong_word_ids)).all()
    elif book_id:
        word_ids = set(
            item.word_id for item in WordBookItem.query.filter_by(wordbook_id=book_id).all()
        )
        words = Word.query.filter(Word.id.in_(word_ids)).all()
    else:
        words = Word.query.all()

    if not words:
        flash("没有可用的单词", "warning")
        return redirect(url_for("quiz.quiz_home"))

    selected = random.sample(words, min(count, len(words)))
    return render_template("quiz_spell.html", words=selected, total=len(selected))


@quiz_bp.route("/submit-mc", methods=["POST"])
def submit_mc():
    """Submit multiple choice quiz answers."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data received"})

    answers = data.get("answers", [])
    results = []
    correct_count = 0

    for ans in answers:
        word_id = ans.get("word_id")
        selected_id = ans.get("selected_id")
        word = Word.query.get(word_id)
        selected_word = Word.query.get(selected_id) if selected_id else None

        is_correct = word_id == selected_id

        if is_correct:
            correct_count += 1
        else:
            # Record wrong answer
            existing = WrongAnswer.query.filter_by(
                word_id=word_id, quiz_type="mc", reviewed=False
            ).first()
            if existing:
                existing.wrong_count += 1
                existing.last_wrong_at = datetime.utcnow()
                existing.user_answer = selected_word.word if selected_word else "(未选择)"
            else:
                wrong = WrongAnswer(
                    word_id=word_id,
                    quiz_type="mc",
                    user_answer=selected_word.word if selected_word else "(未选择)",
                )
                db.session.add(wrong)

            # Update learning record
            record = LearningRecord.query.filter_by(word_id=word_id).first()
            if record:
                record.total_reviews += 1
                record.consecutive_correct = 0

        # Update learning record for correct answers too
        if is_correct:
            record = LearningRecord.query.filter_by(word_id=word_id).first()
            if record:
                record.total_reviews += 1
                record.total_correct += 1

        results.append({
            "word_id": word_id,
            "word": word.word if word else "",
            "definition": word.definition if word else "",
            "is_correct": is_correct,
        })

    db.session.commit()

    total = len(answers)
    return jsonify({
        "success": True,
        "results": results,
        "correct": correct_count,
        "total": total,
        "accuracy": round(correct_count / total * 100, 1) if total > 0 else 0,
    })


@quiz_bp.route("/submit-spell", methods=["POST"])
def submit_spell():
    """Submit spelling quiz answers."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data received"})

    answers = data.get("answers", [])
    results = []
    correct_count = 0

    for ans in answers:
        word_id = ans.get("word_id")
        user_spelling = ans.get("user_answer", "").strip()
        word = Word.query.get(word_id)

        is_correct = user_spelling.lower() == word.word.lower()

        if is_correct:
            correct_count += 1
        else:
            # Record wrong answer
            existing = WrongAnswer.query.filter_by(
                word_id=word_id, quiz_type="spell", reviewed=False
            ).first()
            if existing:
                existing.wrong_count += 1
                existing.last_wrong_at = datetime.utcnow()
                existing.user_answer = user_spelling
            else:
                wrong = WrongAnswer(
                    word_id=word_id,
                    quiz_type="spell",
                    user_answer=user_spelling,
                )
                db.session.add(wrong)

            # Update learning record
            record = LearningRecord.query.filter_by(word_id=word_id).first()
            if record:
                record.total_reviews += 1
                record.consecutive_correct = 0

        # Update learning record for correct answers
        if is_correct:
            record = LearningRecord.query.filter_by(word_id=word_id).first()
            if record:
                record.total_reviews += 1
                record.total_correct += 1

        results.append({
            "word_id": word_id,
            "word": word.word,
            "definition": word.definition,
            "is_correct": is_correct,
            "user_answer": user_spelling,
        })

    db.session.commit()

    total = len(answers)
    return jsonify({
        "success": True,
        "results": results,
        "correct": correct_count,
        "total": total,
        "accuracy": round(correct_count / total * 100, 1) if total > 0 else 0,
    })
