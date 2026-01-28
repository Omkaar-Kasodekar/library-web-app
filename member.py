from flask import Blueprint, render_template, abort, flash
from flask_jwt_extended import jwt_required, get_jwt
from database import get_db
from functools import wraps

member_bp = Blueprint("member", __name__, url_prefix="/member")



def member_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "member":
            flash("You are not authorized to access this page", "error")
            abort(403)
        return fn(*args, **kwargs)
    return wrapper



@member_bp.route("/dashboard")
@member_required
def dashboard():
    return render_template("member/dashboard.html")



@member_bp.route("/books")
@member_required
def books():
    db = get_db()
    books = db.execute(
        "SELECT * FROM books WHERE available = 1 ORDER BY id DESC"
    ).fetchall()

    return render_template("member/books.html", books=books)
