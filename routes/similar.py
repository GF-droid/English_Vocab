"""
Similar words feature using Levenshtein distance for automatic detection
and manual group management for similar-looking words.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Word, SimilarWordGroup, SimilarWordItem, LearningRecord
from sqlalchemy import func

similar_bp = Blueprint("similar", __name__)


@similar_bp.route("/")
def similar_home():
    """Similar words main page - list groups and auto-discover."""
    groups = SimilarWordGroup.query.order_by(SimilarWordGroup.created_at.desc()).all()

    group_data = []
    for g in groups:
        words = [item.word for item in g.items]
        group_data.append({
            "group": g,
            "words": words,
            "word_count": len(words),
        })

    return render_template("similar_words.html", group_data=group_data)


@similar_bp.route("/create", methods=["POST"])
def create_group():
    """Create a new similar word group."""
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()

    if not name:
        flash("组名不能为空", "danger")
        return redirect(url_for("similar.similar_home"))

    group = SimilarWordGroup(name=name, description=description)
    db.session.add(group)
    db.session.commit()

    flash(f'形近词组 "{name}" 已创建', "success")
    return redirect(url_for("similar.group_detail", group_id=group.id))


@similar_bp.route("/<int:group_id>")
def group_detail(group_id):
    """Detail page for a similar word group."""
    group = SimilarWordGroup.query.get_or_404(group_id)
    group_words = [item.word for item in group.items]
    group_word_ids = {w.id for w in group_words}

    # Get all words for adding to group
    all_words = Word.query.order_by(Word.word).all()

    return render_template(
        "similar_group_detail.html",
        group=group,
        group_words=group_words,
        group_word_ids=group_word_ids,
        all_words=all_words,
    )


@similar_bp.route("/<int:group_id>/add-word", methods=["POST"])
def add_word_to_group(group_id):
    """Add a word to a similar word group."""
    group = SimilarWordGroup.query.get_or_404(group_id)
    word_id = request.form.get("word_id", type=int)

    if not word_id:
        flash("请选择单词", "danger")
        return redirect(url_for("similar.group_detail", group_id=group.id))

    existing = SimilarWordItem.query.filter_by(group_id=group_id, word_id=word_id).first()
    if existing:
        flash("该单词已在组内", "warning")
    else:
        item = SimilarWordItem(group_id=group_id, word_id=word_id)
        db.session.add(item)
        db.session.commit()
        flash("已添加到形近词组", "success")

    return redirect(url_for("similar.group_detail", group_id=group.id))


@similar_bp.route("/<int:group_id>/remove-word/<int:word_id>", methods=["POST"])
def remove_word_from_group(group_id, word_id):
    """Remove a word from a similar word group."""
    item = SimilarWordItem.query.filter_by(group_id=group_id, word_id=word_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash("已从形近词组中移除", "success")
    return redirect(url_for("similar.group_detail", group_id=group.id))


@similar_bp.route("/<int:group_id>/delete", methods=["POST"])
def delete_group(group_id):
    """Delete a similar word group."""
    group = SimilarWordGroup.query.get_or_404(group_id)
    name = group.name
    db.session.delete(group)
    db.session.commit()
    flash(f'形近词组 "{name}" 已删除', "success")
    return redirect(url_for("similar.similar_home"))


@similar_bp.route("/discover")
def discover():
    """Auto-discover similar words using Levenshtein distance."""
    threshold = request.args.get("threshold", 2, type=int)
    min_length = request.args.get("min_length", 3, type=int)
    limit = request.args.get("limit", 50, type=int)

    try:
        from Levenshtein import distance as levenshtein_distance
    except ImportError:
        # Fallback to pure Python implementation
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            if len(s2) == 0:
                return len(s1)
            prev = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                curr = [i + 1]
                for j, c2 in enumerate(s2):
                    curr.append(min(
                        prev[j + 1] + 1,
                        curr[j] + 1,
                        prev[j] + (c1 != c2)
                    ))
                prev = curr
            return prev[-1]

    words = Word.query.filter(
        func.length(Word.word) >= min_length
    ).order_by(Word.word).limit(limit).all()

    # Find pairs of similar words
    similar_pairs = []
    seen_pairs = set()

    for i, w1 in enumerate(words):
        for w2 in words[i + 1:]:
            pair_key = tuple(sorted([w1.id, w2.id]))
            if pair_key in seen_pairs:
                continue

            dist = levenshtein_distance(w1.word.lower(), w2.word.lower())
            max_len = max(len(w1.word), len(w2.word))
            # Similar if: distance <= threshold AND not obviously different length
            if dist <= threshold and dist <= max_len * 0.5:
                similar_pairs.append({
                    "word1": w1,
                    "word2": w2,
                    "distance": dist,
                })
                seen_pairs.add(pair_key)

    # Sort by distance
    similar_pairs.sort(key=lambda p: (p["distance"], p["word1"].word))

    return render_template(
        "similar_discover.html",
        similar_pairs=similar_pairs,
        threshold=threshold,
        min_length=min_length,
        limit=limit,
        total_words=Word.query.count(),
    )


@similar_bp.route("/auto-create-group", methods=["POST"])
def auto_create_group():
    """Auto-create a similar word group from discovered pairs."""
    word_ids_str = request.form.get("word_ids", "")
    group_name = request.form.get("name", "").strip()

    if not word_ids_str:
        flash("请选择单词", "danger")
        return redirect(url_for("similar.discover"))

    word_ids = [int(x.strip()) for x in word_ids_str.split(",") if x.strip().isdigit()]
    if len(word_ids) < 2:
        flash("至少需要选择2个单词", "danger")
        return redirect(url_for("similar.discover"))

    # Get words for default name
    words = Word.query.filter(Word.id.in_(word_ids)).all()
    if not group_name:
        group_name = "形近词组: " + ", ".join(w.word for w in words[:3])

    group = SimilarWordGroup(name=group_name)
    db.session.add(group)
    db.session.flush()

    for wid in word_ids:
        db.session.add(SimilarWordItem(group_id=group.id, word_id=wid))

    db.session.commit()
    flash(f'形近词组 "{group_name}" 已创建，包含 {len(word_ids)} 个单词', "success")
    return redirect(url_for("similar.group_detail", group_id=group.id))


@similar_bp.route("/compare/<int:group_id>")
def compare(group_id):
    """Side-by-side comparison of words in a similar group."""
    group = SimilarWordGroup.query.get_or_404(group_id)
    words = [item.word for item in group.items]
    return render_template("similar_compare.html", group=group, words=words)
