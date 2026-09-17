# from functools import wraps
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from sqlalchemy import func, or_
from app.extensions import db
from app.models.user import User
# from app.permissions import login_required


auth_bp = Blueprint("auth", __name__)


@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
        return

    g.user = db.session.get(User, user_id)


# def login_required(view):
#     @wraps(view)
#     def wrapped_view(*args, **kwargs):
#         if g.user is None:
#             return redirect(url_for("auth.login"))

#         return view(*args, **kwargs)

#     return wrapped_view


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if g.user is not None:
        return redirect(url_for("web.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        if len(username) < 3:
            flash("Имя пользователя должно содержать минимум 3 символа.", "error")
        elif len(username) > 50:
            flash("Имя пользователя слишком длинное.", "error")
        elif "@" not in email or len(email) > 120:
            flash("Укажите корректный email.", "error")
        elif len(password) < 8:
            flash("Пароль должен содержать минимум 8 символов.", "error")
        elif password != password_confirm:
            flash("Пароли не совпадают.", "error")
        elif User.query.filter(
            func.lower(User.username) == username.lower()
        ).first():
            flash("Пользователь с таким именем уже существует.", "error")
        elif User.query.filter(
            func.lower(User.email) == email
        ).first():
            flash("Пользователь с таким email уже существует.", "error")
        else:
            user = User(
                username=username,
                email=email,
                role=User.ROLE_STUDENT,
            )

            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            flash(
                "Регистрация завершена. Теперь войдите в аккаунт.",
                "success",
            )

            return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if g.user is not None:
        return redirect(url_for("web.dashboard"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter(
            or_(
                func.lower(User.username) == identifier,
                func.lower(User.email) == identifier,
            )
        ).first()

        if user is None or not user.check_password(password):
            flash("Неверный логин/email или пароль.", "error")
        else:
            session.clear()
            session["user_id"] = user.id

            return redirect(url_for("web.dashboard"))

    return render_template("login.html")


@auth_bp.post("/logout")
def logout():
    session.clear()

    return redirect(url_for("auth.login"))