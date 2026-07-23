from flask import Blueprint

# Blueprints will be imported from their respective modules
main_bp = Blueprint("main", __name__)
study_bp = Blueprint("study", __name__)
quiz_bp = Blueprint("quiz", __name__)
words_bp = Blueprint("words", __name__)
word_books_bp = Blueprint("word_books", __name__)
wrong_book_bp = Blueprint("wrong_book", __name__)
similar_bp = Blueprint("similar", __name__)
api_bp = Blueprint("api", __name__)
