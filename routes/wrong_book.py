from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, WrongAnswer, Word, LearningRecord

wrong_book_bp = Blueprint("wrong_book", __name__)


@wrong_book_bp.route("/")
def wrong_book():
    """Wrong answer notebook - list all wrong answers grouped by word."""
    page = request.args.get("page", 1, type=int)
    quiz_type = request.args.get("type", "")

    # Get unique word IDs with wrong answers
    query = WrongAnswer.query
    if quiz_type:
        query = query.filter_by(quiz_type=quiz_type)

    wrong_words_query = query.with_entities(
        WrongAnswer.word_id,
        db.func.sum(WrongAnswer.wrong_count).label("total_wrong"),
        db.func.max(WrongAnswer.last_wrong_at).label("last_wrong"),
        db.func.min(db.case((WrongAnswer.reviewed == False, 0), else_=1)).label("all_reviewed"),
    ).group_by(WrongAnswer.word_id).order_by(db.text("last_wrong DESC"))

    wrong_words_page = wrong_words_query.paginate(page=page, per_page=20, error_out=False)

    # Enrich with word data
    wrong_words = []
    for row in wrong_words_page.items:
        word = Word.query.get(row.word_id)
        if word:
            wrong_words.append({
                "word": word,
                "total_wrong": row.total_wrong,
                "last_wrong": row.last_wrong,
                "all_reviewed": bool(row.all_reviewed),
            })

    # Stats
    total_wrong_entries = WrongAnswer.query.count()
    unreviewed_count = WrongAnswer.query.filter_by(reviewed=False).count()
    mc_count = WrongAnswer.query.filter_by(quiz_type="mc").count()
    spell_count = WrongAnswer.query.filter_by(quiz_type="spell").count()

    return render_template(
        "wrong_book.html",
        wrong_words=wrong_words,
        pagination=wrong_words_page,
        total_wrong_entries=total_wrong_entries,
        unreviewed_count=unreviewed_count,
        mc_count=mc_count,
        spell_count=spell_count,
        current_type=quiz_type,
    )


@wrong_book_bp.route("/<int:word_id>/details")
def word_wrong_details(word_id):
    """Get all wrong answer details for a specific word."""
    word = Word.query.get_or_404(word_id)
    wrongs = WrongAnswer.query.filter_by(word_id=word_id).order_by(
        WrongAnswer.last_wrong_at.desc()
    ).all()
    return render_template("wrong_word_detail.html", word=word, wrongs=wrongs)


@wrong_book_bp.route("/<int:wrong_id>/mark-reviewed", methods=["POST"])
def mark_reviewed(wrong_id):
    """Mark a wrong answer as reviewed."""
    wrong = WrongAnswer.query.get_or_404(wrong_id)
    wrong.reviewed = True
    db.session.commit()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})
    flash("已标记为已复习", "success")
    return redirect(url_for("wrong_book.wrong_book"))


@wrong_book_bp.route("/mark-all-reviewed", methods=["POST"])
def mark_all_reviewed():
    """Mark all wrong answers as reviewed."""
    word_id = request.form.get("word_id", type=int)
    query = WrongAnswer.query.filter_by(reviewed=False)
    if word_id:
        query = query.filter_by(word_id=word_id)

    count = query.update({"reviewed": True})
    db.session.commit()
    flash(f"已标记 {count} 条记录为已复习", "success")
    return redirect(url_for("wrong_book.wrong_book"))


@wrong_book_bp.route("/<int:wrong_id>/delete", methods=["POST"])
def delete_wrong(wrong_id):
    """Delete a wrong answer record."""
    wrong = WrongAnswer.query.get_or_404(wrong_id)
    db.session.delete(wrong)
    db.session.commit()
    flash("已删除错题记录", "success")
    return redirect(url_for("wrong_book.wrong_book"))
