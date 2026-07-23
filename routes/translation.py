import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, TranslationPassage, TranslationAttempt
from routes.ai_helper import call_ai, SYSTEM_PROMPT_GRADER

translation_bp = Blueprint("translation", __name__)


@translation_bp.route("/")
def home():
    """Translation practice home — list all passages."""
    passages = TranslationPassage.query.order_by(
        TranslationPassage.created_at.desc()
    ).all()

    passage_data = []
    for p in passages:
        last_attempt = p.attempts[0] if p.attempts else None
        passage_data.append({
            "passage": p,
            "attempt_count": len(p.attempts),
            "best_score": max((a.ai_score for a in p.attempts), default=None),
            "last_attempt": last_attempt,
        })

    return render_template("translation_home.html", passages=passage_data)


@translation_bp.route("/import", methods=["GET", "POST"])
def import_passage():
    """Import a new passage for translation practice."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        source = request.form.get("source", "").strip()

        if not title or not content:
            flash("标题和内容不能为空", "danger")
            return redirect(url_for("translation.import_passage"))

        passage = TranslationPassage(title=title, content=content, source=source)
        db.session.add(passage)
        db.session.commit()

        flash(f'✅ 文章 "{title}" 已导入', "success")
        return redirect(url_for("translation.practice", passage_id=passage.id))

    return render_template("translation_import.html")


@translation_bp.route("/practice/<int:passage_id>")
def practice(passage_id):
    """Practice translating a passage."""
    passage = TranslationPassage.query.get_or_404(passage_id)

    # Split content into paragraphs for easier translation
    paragraphs = [p.strip() for p in passage.content.split("\n") if p.strip()]

    if not paragraphs:
        paragraphs = [passage.content]

    # Previous attempts
    attempts = TranslationAttempt.query.filter_by(
        passage_id=passage_id
    ).order_by(TranslationAttempt.created_at.desc()).all()

    return render_template(
        "translation_practice.html",
        passage=passage,
        paragraphs=paragraphs,
        attempts=attempts,
    )


@translation_bp.route("/attempt/<int:attempt_id>")
def view_attempt(attempt_id):
    """View a specific translation attempt's details."""
    attempt = TranslationAttempt.query.get_or_404(attempt_id)
    return render_template("translation_practice.html",
                           passage=attempt.passage,
                           paragraphs=[attempt.passage.content],
                           attempts=attempt.passage.attempts,
                           highlight_attempt=attempt)


@translation_bp.route("/delete/<int:passage_id>", methods=["POST"])
def delete_passage(passage_id):
    """Delete a passage and its attempts."""
    passage = TranslationPassage.query.get_or_404(passage_id)
    title = passage.title
    db.session.delete(passage)
    db.session.commit()
    flash(f'文章 "{title}" 已删除', "success")
    return redirect(url_for("translation.home"))
