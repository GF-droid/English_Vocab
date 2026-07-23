from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, WordBook, WordBookItem, Word, LearningRecord

word_books_bp = Blueprint("word_books", __name__)


@word_books_bp.route("/")
def book_list():
    """List all word books."""
    books = WordBook.query.order_by(WordBook.created_at.desc()).all()

    # Build progress data for each book
    book_stats = []
    for book in books:
        total = book.word_count
        learned = book.learned_count
        mastered = book.mastered_count
        book_stats.append({
            "book": book,
            "total": total,
            "learned": learned,
            "mastered": mastered,
            "progress": round(learned / total * 100) if total > 0 else 0,
            "mastery": round(mastered / total * 100) if total > 0 else 0,
        })

    return render_template("word_books.html", book_stats=book_stats)


@word_books_bp.route("/create", methods=["POST"])
def create_book():
    """Create a new word book."""
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    cover_color = request.form.get("cover_color", "#4A90D9")

    if not name:
        flash("单词书名称不能为空", "danger")
        return redirect(url_for("word_books.book_list"))

    book = WordBook(name=name, description=description, cover_color=cover_color)
    db.session.add(book)
    db.session.commit()

    flash(f'单词书 "{name}" 已创建', "success")
    return redirect(url_for("word_books.book_detail", book_id=book.id))


@word_books_bp.route("/<int:book_id>")
def book_detail(book_id):
    """Word book detail page."""
    book = WordBook.query.get_or_404(book_id)

    page = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "added")

    # Build query for words in this book
    if sort == "word":
        items_query = WordBookItem.query.filter_by(wordbook_id=book_id).join(
            Word, WordBookItem.word_id == Word.id
        ).order_by(Word.word.asc())
    elif sort == "status":
        items_query = WordBookItem.query.filter_by(wordbook_id=book_id).outerjoin(
            LearningRecord, WordBookItem.word_id == LearningRecord.word_id
        ).order_by(LearningRecord.status.asc().nullsfirst(), Word.word.asc())
    else:
        items_query = WordBookItem.query.filter_by(wordbook_id=book_id).order_by(
            WordBookItem.added_at.desc()
        )

    items = items_query.paginate(page=page, per_page=30, error_out=False)

    # Word IDs already in this book
    book_word_ids = set(
        item.word_id for item in WordBookItem.query.filter_by(wordbook_id=book_id).all()
    )

    return render_template(
        "word_book_detail.html",
        book=book,
        items=items,
        current_sort=sort,
        book_word_ids=book_word_ids,
    )


@word_books_bp.route("/<int:book_id>/edit", methods=["POST"])
def edit_book(book_id):
    """Edit a word book."""
    book = WordBook.query.get_or_404(book_id)

    book.name = request.form.get("name", book.name).strip()
    book.description = request.form.get("description", book.description).strip()
    book.cover_color = request.form.get("cover_color", book.cover_color)

    if not book.name:
        flash("单词书名称不能为空", "danger")
        return redirect(url_for("word_books.book_detail", book_id=book.id))

    db.session.commit()
    flash(f'单词书 "{book.name}" 已更新', "success")
    return redirect(url_for("word_books.book_detail", book_id=book.id))


@word_books_bp.route("/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """Delete a word book."""
    book = WordBook.query.get_or_404(book_id)
    name = book.name
    db.session.delete(book)
    db.session.commit()
    flash(f'单词书 "{name}" 已删除', "success")
    return redirect(url_for("word_books.book_list"))


@word_books_bp.route("/<int:book_id>/add-words", methods=["POST"])
def add_words_to_book(book_id):
    """Add words to a book by ID list."""
    book = WordBook.query.get_or_404(book_id)
    word_ids_str = request.form.get("word_ids", "")
    word_text = request.form.get("word_text", "").strip()

    added = 0
    skipped = 0

    # Add by comma-separated IDs
    if word_ids_str:
        for part in word_ids_str.split(","):
            part = part.strip()
            if part.isdigit():
                wid = int(part)
                existing = WordBookItem.query.filter_by(
                    wordbook_id=book_id, word_id=wid
                ).first()
                if not existing and Word.query.get(wid):
                    db.session.add(WordBookItem(wordbook_id=book_id, word_id=wid))
                    added += 1
                else:
                    skipped += 1

    # Add by word text (comma or newline separated)
    if word_text:
        for line in word_text.replace("\n", ",").split(","):
            w = line.strip()
            if not w:
                continue
            word_obj = Word.query.filter_by(word=w).first()
            if word_obj:
                existing = WordBookItem.query.filter_by(
                    wordbook_id=book_id, word_id=word_obj.id
                ).first()
                if not existing:
                    db.session.add(WordBookItem(wordbook_id=book_id, word_id=word_obj.id))
                    added += 1
                else:
                    skipped += 1

    db.session.commit()
    flash(f"已添加 {added} 个单词" + (f"，跳过 {skipped} 个已存在的单词" if skipped else ""), "success")
    return redirect(url_for("word_books.book_detail", book_id=book.id))


@word_books_bp.route("/<int:book_id>/remove-word/<int:word_id>", methods=["POST"])
def remove_word_from_book(book_id, word_id):
    """Remove a word from a book."""
    item = WordBookItem.query.filter_by(wordbook_id=book_id, word_id=word_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash("已从单词书中移除", "success")
    return redirect(url_for("word_books.book_detail", book_id=book_id))
