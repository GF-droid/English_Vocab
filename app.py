from flask import Flask
from config import Config
from models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Register blueprints
    from routes.main import main_bp
    from routes.study import study_bp
    from routes.quiz import quiz_bp
    from routes.words import words_bp
    from routes.word_books import word_books_bp
    from routes.wrong_book import wrong_book_bp
    from routes.similar import similar_bp
    from routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(study_bp, url_prefix="/study")
    app.register_blueprint(quiz_bp, url_prefix="/quiz")
    app.register_blueprint(words_bp, url_prefix="/words")
    app.register_blueprint(word_books_bp, url_prefix="/word-books")
    app.register_blueprint(wrong_book_bp, url_prefix="/wrong-book")
    app.register_blueprint(similar_bp, url_prefix="/similar")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Context processor for templates
    @app.context_processor
    def inject_globals():
        from models import WordBook
        return {
            "get_book_options": lambda: WordBook.query.order_by(WordBook.name).all()
        }

    # Create tables
    with app.app_context():
        db.create_all()

    # Ensure audio directory exists
    import os
    os.makedirs(app.config["AUDIO_DIR"], exist_ok=True)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
