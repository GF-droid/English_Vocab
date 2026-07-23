from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Word, LearningRecord, DailyCheckin, WordBook, WordBookItem
from spaced_repetition import sm2_algorithm, get_quality_label
from config import Config

study_bp = Blueprint("study", __name__)


@study_bp.route("/")
def study_home():
    """Daily study page - shows words due for review."""
    today = date.today()

    # Get words due for review
    due_records = (
        LearningRecord.query
        .filter(LearningRecord.next_review <= today)
        .order_by(LearningRecord.ease_factor.asc())
        .limit(Config.WORDS_PER_SESSION)
        .all()
    )

    due_words = []
    for record in due_records:
        due_words.append({
            "record_id": record.id,
            "word": record.word,
            "ease_factor": record.ease_factor,
            "interval": record.interval_days,
            "repetitions": record.repetitions,
            "status": record.status,
        })

    # Check for new words available to learn
    new_words_available = 0
    learned_word_ids = set(
        r.word_id for r in LearningRecord.query.all()
    )
    if learned_word_ids:
        new_words_available = Word.query.filter(
            ~Word.id.in_(learned_word_ids)
        ).count()
    else:
        new_words_available = Word.query.count()

    # Today's progress
    today_checkin = DailyCheckin.query.filter_by(checkin_date=today).first()
    reviewed_today = today_checkin.reviewed_count if today_checkin else 0

    return render_template(
        "study.html",
        due_words=due_words,
        due_count=len(due_words),
        new_words_available=new_words_available,
        reviewed_today=reviewed_today,
        quality_labels={i: get_quality_label(i) for i in range(6)},
    )


@study_bp.route("/rate", methods=["POST"])
def rate_word():
    """Submit a rating for a word after review."""
    record_id = request.form.get("record_id", type=int)
    quality = request.form.get("quality", type=int)

    if record_id is None or quality is None:
        flash("Invalid request", "danger")
        return redirect(url_for("study.study_home"))

    record = LearningRecord.query.get_or_404(record_id)
    word = record.word

    # Apply SM-2 algorithm
    result = sm2_algorithm(
        ease_factor=record.ease_factor,
        interval=record.interval_days,
        repetitions=record.repetitions,
        quality=quality,
    )

    # Update record
    record.ease_factor = result["ease_factor"]
    record.interval_days = result["interval"]
    record.repetitions = result["repetitions"]
    record.next_review = result["next_review"]
    record.last_review = date.today()
    record.total_reviews += 1
    if quality >= 3:
        record.total_correct += 1
        record.consecutive_correct += 1
    else:
        record.consecutive_correct = 0

    # Update status
    if record.repetitions >= 5 and record.ease_factor >= 2.5:
        record.status = "mastered"
    elif record.repetitions >= 2:
        record.status = "reviewing"
    else:
        record.status = "learning"

    # Update daily check-in
    today = date.today()
    checkin = DailyCheckin.query.filter_by(checkin_date=today).first()
    if not checkin:
        checkin = DailyCheckin(checkin_date=today, reviewed_count=0, new_words_count=0)
        db.session.add(checkin)
    if checkin.reviewed_count is None:
        checkin.reviewed_count = 0
    checkin.reviewed_count += 1

    db.session.commit()

    # Check if this is an AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "success": True,
            "next_review": result["next_review"].isoformat(),
            "ease_factor": result["ease_factor"],
            "interval": result["interval"],
            "status": record.status,
        })

    flash(f'"{word.word}" 评分完成！下次复习: {result["next_review"]}', "success")
    return redirect(url_for("study.study_home"))


@study_bp.route("/add-new", methods=["POST"])
def add_new_word():
    """Introduce a new word into the learning queue."""
    word_id = request.form.get("word_id", type=int)

    if word_id:
        word = Word.query.get_or_404(word_id)
    else:
        # Pick a random unlearned word
        learned_ids = set(r.word_id for r in LearningRecord.query.all())
        if learned_ids:
            word = Word.query.filter(~Word.id.in_(learned_ids)).order_by(db.func.random()).first()
        else:
            word = Word.query.order_by(db.func.random()).first()

    if not word:
        flash("没有可用的新单词了", "warning")
        return redirect(url_for("study.study_home"))

    # Check if already has a learning record
    existing = LearningRecord.query.filter_by(word_id=word.id).first()
    if existing:
        flash(f'"{word.word}" 已经在学习队列中', "info")
        return redirect(url_for("study.study_home"))

    record = LearningRecord(word_id=word.id)
    db.session.add(record)

    # Update daily check-in
    today = date.today()
    checkin = DailyCheckin.query.filter_by(checkin_date=today).first()
    if not checkin:
        checkin = DailyCheckin(checkin_date=today, reviewed_count=0, new_words_count=0)
        db.session.add(checkin)
    if checkin.new_words_count is None:
        checkin.new_words_count = 0
    checkin.new_words_count += 1

    db.session.commit()

    flash(f'新单词 "{word.word}" 已加入学习队列！', "success")
    return redirect(url_for("study.study_home"))


@study_bp.route("/new-words-select")
def new_words_select():
    """Page to select new words to learn."""
    learned_ids = set(r.word_id for r in LearningRecord.query.all())

    page = request.args.get("page", 1, type=int)
    per_page = 50

    book_id = request.args.get("book_id", type=int)

    query = Word.query
    if learned_ids:
        query = query.filter(~Word.id.in_(learned_ids))
    if book_id:
        book_word_ids = set(
            item.word_id for item in WordBookItem.query.filter_by(wordbook_id=book_id).all()
        )
        query = query.filter(Word.id.in_(book_word_ids))

    words = query.order_by(Word.word).paginate(page=page, per_page=per_page, error_out=False)
    word_books = WordBook.query.order_by(WordBook.name).all()

    return render_template(
        "new_words_select.html",
        words=words,
        word_books=word_books,
        current_book_id=book_id,
        already_learned=len(learned_ids),
    )
