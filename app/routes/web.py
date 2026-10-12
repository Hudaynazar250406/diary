from flask import Blueprint, redirect, render_template, url_for

from app.permissions import login_required


web_bp = Blueprint("web", __name__)


@web_bp.get("/")
def index():
    return redirect(url_for("web.dashboard"))


@web_bp.get("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")