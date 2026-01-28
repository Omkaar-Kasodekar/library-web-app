from flask import Flask, redirect, url_for, flash
from flask_jwt_extended import JWTManager, get_jwt, jwt_required
from database import close_db, init_db
from auth import auth_bp
from admin import admin_bp
from member import member_bp

def create_app():
    app = Flask(__name__)

    
    app.config["SECRET_KEY"] = "super-secret-key"
    app.config["JWT_SECRET_KEY"] = "jwt-secret-key"


    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_SECURE"] = False          
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False   
    app.config["JWT_ACCESS_COOKIE_PATH"] = "/"

    jwt = JWTManager(app)

    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(member_bp)

   
    app.teardown_appcontext(close_db)

  
    @app.route("/")
    @jwt_required(optional=True)
    def index():
        claims = get_jwt()
        if not claims:
            return redirect(url_for("auth.login"))

        if claims.get("role") == "admin":
            return redirect(url_for("admin.dashboard"))

        return redirect(url_for("member.dashboard"))

    
    @app.errorhandler(403)
    def forbidden(e):
        flash("Access denied", "error")
        return redirect(url_for("auth.login"))

    return app


if __name__ == "__main__":
    app = create_app()
    init_db()
    app.run(debug=True)
