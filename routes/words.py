from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Word, LearningRecord, WrongAnswer, WordBook, WordBookItem, SimilarWordItem
from sqlalchemy import or_

words_bp = Blueprint("words", __name__)


@words_bp.route("/search")
def search():
    """Word search page with filters."""
    query = request.args.get("q", "").strip()
    book_id = request.args.get("book_id", type=int)
    status_filter = request.args.get("status", "")
    pos_filter = request.args.get("pos", "")
    sort = request.args.get("sort", "word")
    page = request.args.get("page", 1, type=int)

    word_query = Word.query

    # Text search
    if query:
        search_term = f"%{query}%"
        word_query = word_query.filter(
            or_(
                Word.word.ilike(search_term),
                Word.definition.ilike(search_term),
                Word.phonetic.ilike(search_term),
            )
        )

    # Book filter
    if book_id:
        book_word_ids = set(
            item.word_id for item in WordBookItem.query.filter_by(wordbook_id=book_id).all()
        )
        word_query = word_query.filter(Word.id.in_(book_word_ids))

    # Status filter
    if status_filter:
        if status_filter == "mastered":
            mastered_ids = set(
                r.word_id for r in LearningRecord.query.filter_by(status="mastered").all()
            )
            word_query = word_query.filter(Word.id.in_(mastered_ids))
        elif status_filter == "learning":
            learning_ids = set(
                r.word_id for r in LearningRecord.query.filter(
                    LearningRecord.status.in_(["learning", "reviewing"])
                ).all()
            )
            word_query = word_query.filter(Word.id.in_(learning_ids))
        elif status_filter == "not_started":
            learned_ids = set(r.word_id for r in LearningRecord.query.all())
            if learned_ids:
                word_query = word_query.filter(~Word.id.in_(learned_ids))

    # POS filter
    if pos_filter:
        word_query = word_query.filter(Word.part_of_speech.ilike(f"%{pos_filter}%"))

    # Sorting
    if sort == "newest":
        word_query = word_query.order_by(Word.created_at.desc())
    elif sort == "oldest":
        word_query = word_query.order_by(Word.created_at.asc())
    else:
        word_query = word_query.order_by(Word.word.asc())

    words = word_query.paginate(page=page, per_page=30, error_out=False)
    word_books = WordBook.query.order_by(WordBook.name).all()

    return render_template(
        "search.html",
        words=words,
        word_books=word_books,
        query=query,
        current_book_id=book_id,
        current_status=status_filter,
        current_pos=pos_filter,
        current_sort=sort,
    )


@words_bp.route("/<int:word_id>")
def word_detail(word_id):
    """Word detail page with learning history and related info."""
    word = Word.query.get_or_404(word_id)

    # Learning record
    learning = LearningRecord.query.filter_by(word_id=word.id).first()

    # Wrong answers
    wrongs = WrongAnswer.query.filter_by(word_id=word.id).order_by(
        WrongAnswer.last_wrong_at.desc()
    ).all()

    # Similar words (from similar word groups)
    similar_group_items = SimilarWordItem.query.filter_by(word_id=word.id).all()
    similar_words = []
    for item in similar_group_items:
        group_items = SimilarWordItem.query.filter(
            SimilarWordItem.group_id == item.group_id,
            SimilarWordItem.word_id != word.id
        ).all()
        for gi in group_items:
            if gi.word not in similar_words:
                similar_words.append(gi.word)

    # Which word books contain this word
    containing_books = WordBook.query.join(
        WordBookItem, WordBookItem.wordbook_id == WordBook.id
    ).filter(WordBookItem.word_id == word.id).all()

    # All books (for "add to book" action)
    all_books = WordBook.query.order_by(WordBook.name).all()

    return render_template(
        "word_detail.html",
        word=word,
        learning=learning,
        wrongs=wrongs,
        similar_words=similar_words,
        containing_books=containing_books,
        all_books=all_books,
    )


@words_bp.route("/add", methods=["POST"])
def add_word():
    """Add a new word to the database."""
    word_text = request.form.get("word", "").strip()
    phonetic = request.form.get("phonetic", "").strip()
    definition = request.form.get("definition", "").strip()
    example_sentence = request.form.get("example_sentence", "").strip()
    example_translation = request.form.get("example_translation", "").strip()
    part_of_speech = request.form.get("part_of_speech", "").strip()
    tags = request.form.get("tags", "").strip()
    book_id = request.form.get("book_id", type=int)

    if not word_text or not definition:
        flash("单词和释义不能为空", "danger")
        return redirect(request.referrer or url_for("words.search"))

    # Check for duplicate
    existing = Word.query.filter_by(word=word_text).first()
    if existing:
        flash(f'单词 "{word_text}" 已存在', "warning")
        # Still add to book if specified
        if book_id:
            _add_to_book(existing.id, book_id)
        return redirect(url_for("words.word_detail", word_id=existing.id))

    word = Word(
        word=word_text,
        phonetic=phonetic,
        definition=definition,
        example_sentence=example_sentence,
        example_translation=example_translation,
        part_of_speech=part_of_speech,
        tags=tags,
    )
    db.session.add(word)
    db.session.flush()  # Get the ID

    # Add to book if specified
    if book_id:
        _add_to_book(word.id, book_id)

    db.session.commit()
    flash(f'单词 "{word_text}" 已添加', "success")
    return redirect(url_for("words.word_detail", word_id=word.id))


@words_bp.route("/<int:word_id>/edit", methods=["POST"])
def edit_word(word_id):
    """Edit an existing word."""
    word = Word.query.get_or_404(word_id)

    word.word = request.form.get("word", word.word).strip()
    word.phonetic = request.form.get("phonetic", word.phonetic).strip()
    word.definition = request.form.get("definition", word.definition).strip()
    word.example_sentence = request.form.get("example_sentence", word.example_sentence).strip()
    word.example_translation = request.form.get("example_translation", word.example_translation).strip()
    word.part_of_speech = request.form.get("part_of_speech", word.part_of_speech).strip()
    word.tags = request.form.get("tags", word.tags).strip()

    db.session.commit()
    flash(f'单词 "{word.word}" 已更新', "success")
    return redirect(url_for("words.word_detail", word_id=word.id))


@words_bp.route("/<int:word_id>/delete", methods=["POST"])
def delete_word(word_id):
    """Delete a word."""
    word = Word.query.get_or_404(word_id)
    word_text = word.word
    db.session.delete(word)
    db.session.commit()
    flash(f'单词 "{word_text}" 已删除', "success")
    return redirect(url_for("words.search"))


@words_bp.route("/<int:word_id>/add-to-book", methods=["POST"])
def add_word_to_book(word_id):
    """Add a word to a word book."""
    book_id = request.form.get("book_id", type=int)
    if not book_id:
        flash("请选择单词书", "danger")
        return redirect(url_for("words.word_detail", word_id=word_id))

    _add_to_book(word_id, book_id)
    db.session.commit()
    flash("已添加到单词书", "success")
    return redirect(url_for("words.word_detail", word_id=word_id))


def _add_to_book(word_id, book_id):
    """Helper: add word to book if not already there."""
    existing = WordBookItem.query.filter_by(
        wordbook_id=book_id, word_id=word_id
    ).first()
    if not existing:
        item = WordBookItem(wordbook_id=book_id, word_id=word_id)
        db.session.add(item)
