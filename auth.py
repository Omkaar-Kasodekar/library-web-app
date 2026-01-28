from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies
)
import bcrypt
from database import get_db

auth_bp = Blueprint("auth", __name__)



@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password", "").encode()

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

       
        if not user or not bcrypt.checkpw(password, user["password"]):
            flash("Invalid username or password", "error")
            return redirect(url_for("auth.login"))

       
        access_token = create_access_token(
            identity=str(user["id"]),
            additional_claims={
                "username": user["username"],
                "role": user["role"]
            }
        )

       
        if user["role"] == "admin":
            redirect_url = url_for("admin.dashboard")
        else:
            redirect_url = url_for("member.dashboard")

        resp = make_response(redirect(redirect_url))
        set_access_cookies(resp, access_token)

        flash("Login successful", "success")
        return resp

    return render_template("login.html")



@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password", "").encode()

        if not username or not password:
            flash("All fields are required", "error")
            return redirect(url_for("auth.register"))

        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        db = get_db()

        try:
            db.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, hashed, "member")
            )
            db.commit()
        except Exception:
            flash("Username already exists", "error")
            return redirect(url_for("auth.register"))

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")



@auth_bp.route("/logout")
def logout():
    resp = make_response(redirect(url_for("auth.login")))
    unset_jwt_cookies(resp)
    flash("You have been logged out", "success")
    return resp
