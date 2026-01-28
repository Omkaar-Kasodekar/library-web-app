from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_jwt_extended import jwt_required, get_jwt
from database import get_db
from functools import wraps

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")



def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "admin":
            flash("You are not authorized to access this page", "error")
            abort(403)
        return fn(*args, **kwargs)
    return wrapper



@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    db = get_db()
    total_books = db.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]

    return render_template(
        "admin/dashboard.html",
        total_books=total_books
    )


@admin_bp.route("/books", methods=["GET", "POST"])
@admin_required
def books():
    db = get_db()

    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")

        if not title or not author:
            flash("Title and Author are required", "error")
        else:
            db.execute(
                "INSERT INTO books (title, author) VALUES (?, ?)",
                (title, author)
            )
            db.commit()
            flash("Book added successfully", "success")

        return redirect(url_for("admin.books"))

    books = db.execute(
        "SELECT * FROM books ORDER BY id DESC"
    ).fetchall()

    return render_template("admin/books.html", books=books)




