from datetime import date, timedelta
from flask import Blueprint, render_template, jsonify
from models import db, Word, LearningRecord, WrongAnswer, DailyCheckin, WordBook

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Dashboard homepage."""
    today = date.today()

    # Today's due words
    due_count = LearningRecord.query.filter(
        LearningRecord.next_review <= today
    ).count()

    # Total words
    total_words = Word.query.count()

    # Mastered words
    mastered_count = LearningRecord.query.filter_by(status="mastered").count()

    # Wrong answers not yet reviewed
    wrong_count = WrongAnswer.query.filter_by(reviewed=False).count()

    # Today's check-in
    today_checkin = DailyCheckin.query.filter_by(checkin_date=today).first()
    reviewed_today = today_checkin.reviewed_count if today_checkin else 0

    # Streak calculation
    streak = _calculate_streak()

    # Word books
    word_books = WordBook.query.order_by(WordBook.created_at.desc()).all()

    # Recent 30 days activity
    thirty_days_ago = today - timedelta(days=29)
    checkins = DailyCheckin.query.filter(
        DailyCheckin.checkin_date >= thirty_days_ago
    ).order_by(DailyCheckin.checkin_date.asc()).all()

    activity_data = []
    for i in range(30):
        d = thirty_days_ago + timedelta(days=i)
        entry = next((c for c in checkins if c.checkin_date == d), None)
        activity_data.append({
            "date": d.isoformat(),
            "count": entry.reviewed_count if entry else 0,
        })

    # Recent wrong answers for quick view
    recent_wrongs = (
        WrongAnswer.query
        .filter_by(reviewed=False)
        .order_by(WrongAnswer.last_wrong_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "index.html",
        due_count=due_count,
        total_words=total_words,
        mastered_count=mastered_count,
        wrong_count=wrong_count,
        reviewed_today=reviewed_today,
        streak=streak,
        word_books=word_books,
        activity_data=activity_data,
        recent_wrongs=recent_wrongs,
    )


@main_bp.route("/stats")
def stats():
    """Learning statistics page."""
    today = date.today()
    total_words = Word.query.count()
    total_books = WordBook.query.count()
    mastered = LearningRecord.query.filter_by(status="mastered").count()
    learning = LearningRecord.query.filter_by(status="learning").count()
    reviewing = LearningRecord.query.filter_by(status="reviewing").count()
    not_started = total_words - mastered - learning - reviewing

    # Total reviews
    total_reviews = db.session.query(
        db.func.sum(LearningRecord.total_reviews)
    ).scalar() or 0

    # 30 day review trend
    thirty_days_ago = today - timedelta(days=29)
    checkins = DailyCheckin.query.filter(
        DailyCheckin.checkin_date >= thirty_days_ago
    ).order_by(DailyCheckin.checkin_date.asc()).all()

    daily_labels = []
    daily_reviews = []
    daily_new = []
    for i in range(30):
        d = thirty_days_ago + timedelta(days=i)
        entry = next((c for c in checkins if c.checkin_date == d), None)
        daily_labels.append(d.strftime("%m/%d"))
        daily_reviews.append(entry.reviewed_count if entry else 0)
        daily_new.append(entry.new_words_count if entry else 0)

    # Book progress
    books = WordBook.query.all()
    book_data = []
    for book in books:
        total = book.word_count
        if total > 0:
            m = book.mastered_count
            l = book.learned_count
            book_data.append({
                "name": book.name,
                "total": total,
                "learned": l,
                "mastered": m,
                "color": book.cover_color,
            })

    # Wrong answer stats
    wrong_total = WrongAnswer.query.count()
    wrong_unreviewed = WrongAnswer.query.filter_by(reviewed=False).count()
    wrong_mc = WrongAnswer.query.filter_by(quiz_type="mc").count()
    wrong_spell = WrongAnswer.query.filter_by(quiz_type="spell").count()

    return render_template(
        "stats.html",
        total_words=total_words,
        total_books=total_books,
        mastered=mastered,
        learning=learning,
        reviewing=reviewing,
        not_started=not_started,
        total_reviews=total_reviews,
        daily_labels=daily_labels,
        daily_reviews=daily_reviews,
        daily_new=daily_new,
        book_data=book_data,
        wrong_total=wrong_total,
        wrong_unreviewed=wrong_unreviewed,
        wrong_mc=wrong_mc,
        wrong_spell=wrong_spell,
    )


@main_bp.route("/import-export")
def import_export():
    """Import/export page."""
    word_books = WordBook.query.order_by(WordBook.name).all()
    return render_template("import_export.html", word_books=word_books)


def _calculate_streak():
    """Calculate the current consecutive daily check-in streak."""
    today = date.today()
    streak = 0
    current = today
    while True:
        checkin = DailyCheckin.query.filter_by(checkin_date=current).first()
        if checkin:
            streak += 1
            current = current - timedelta(days=1)
        else:
            break
    # If today hasn't been checked in yet, check if yesterday starts the streak
    if streak == 0:
        current = today - timedelta(days=1)
        while True:
            checkin = DailyCheckin.query.filter_by(checkin_date=current).first()
            if checkin:
                streak += 1
                current = current - timedelta(days=1)
            else:
                break
    return streak
