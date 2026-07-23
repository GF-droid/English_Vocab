from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, Float, Date, DateTime, ForeignKey, Boolean

db = SQLAlchemy()


class Word(db.Model):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    word: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    phonetic: Mapped[str] = mapped_column(String(200), default="")
    definition: Mapped[str] = mapped_column(Text, nullable=False)
    example_sentence: Mapped[str] = mapped_column(Text, default="")
    example_translation: Mapped[str] = mapped_column(Text, default="")
    part_of_speech: Mapped[str] = mapped_column(String(50), default="")
    audio_path: Mapped[str] = mapped_column(String(500), default="")
    tags: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    learning_record = relationship("LearningRecord", back_populates="word", uselist=False,
                                   cascade="all, delete-orphan")
    wordbook_items = relationship("WordBookItem", back_populates="word", cascade="all, delete-orphan")
    wrong_answers = relationship("WrongAnswer", back_populates="word", cascade="all, delete-orphan")
    similar_word_items = relationship("SimilarWordItem", back_populates="word", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "word": self.word,
            "phonetic": self.phonetic,
            "definition": self.definition,
            "example_sentence": self.example_sentence,
            "example_translation": self.example_translation,
            "part_of_speech": self.part_of_speech,
            "tags": self.tags.split(",") if self.tags else [],
        }


class WordBook(db.Model):
    __tablename__ = "word_books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    cover_color: Mapped[str] = mapped_column(String(20), default="#4A90D9")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    items = relationship("WordBookItem", back_populates="wordbook", cascade="all, delete-orphan")

    @property
    def word_count(self):
        return len(self.items)

    @property
    def learned_count(self):
        from sqlalchemy import select
        from flask_sqlalchemy import SQLAlchemy
        return sum(
            1 for item in self.items
            if item.word.learning_record and item.word.learning_record.repetitions > 0
        )

    @property
    def mastered_count(self):
        return sum(
            1 for item in self.items
            if item.word.learning_record and item.word.learning_record.status == "mastered"
        )


class WordBookItem(db.Model):
    __tablename__ = "word_book_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wordbook_id: Mapped[int] = mapped_column(ForeignKey("word_books.id"), nullable=False)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    wordbook = relationship("WordBook", back_populates="items")
    word = relationship("Word", back_populates="wordbook_items")


class LearningRecord(db.Model):
    __tablename__ = "learning_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"), unique=True, nullable=False)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval_days: Mapped[int] = mapped_column(Integer, default=0)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    next_review: Mapped[date] = mapped_column(Date, default=date.today)
    last_review: Mapped[date] = mapped_column(Date, nullable=True)
    consecutive_correct: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="learning")  # learning, reviewing, mastered
    total_reviews: Mapped[int] = mapped_column(Integer, default=0)
    total_correct: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    word = relationship("Word", back_populates="learning_record")

    @property
    def accuracy(self):
        if self.total_reviews == 0:
            return 0
        return round(self.total_correct / self.total_reviews * 100, 1)

    @property
    def is_due(self):
        return self.next_review <= date.today()


class WrongAnswer(db.Model):
    __tablename__ = "wrong_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"), nullable=False)
    quiz_type: Mapped[str] = mapped_column(String(20), default="mc")  # mc, spell
    user_answer: Mapped[str] = mapped_column(Text, default="")
    wrong_count: Mapped[int] = mapped_column(Integer, default=1)
    last_wrong_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reviewed: Mapped[bool] = mapped_column(Boolean, default=False)

    word = relationship("Word", back_populates="wrong_answers")


class SimilarWordGroup(db.Model):
    __tablename__ = "similar_word_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items = relationship("SimilarWordItem", back_populates="group", cascade="all, delete-orphan")

    @property
    def word_count(self):
        return len(self.items)


class SimilarWordItem(db.Model):
    __tablename__ = "similar_word_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("similar_word_groups.id"), nullable=False)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"), nullable=False)

    group = relationship("SimilarWordGroup", back_populates="items")
    word = relationship("Word", back_populates="similar_word_items")


class DailyCheckin(db.Model):
    __tablename__ = "daily_checkins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    checkin_date: Mapped[date] = mapped_column(Date, default=date.today, unique=True)
    reviewed_count: Mapped[int] = mapped_column(Integer, default=0)
    new_words_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
