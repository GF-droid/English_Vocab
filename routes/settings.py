from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, AISettings

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/")
def settings_page():
    """AI and application settings page."""
    ai = AISettings.query.first()
    return render_template("settings.html", ai=ai)


@settings_bp.route("/ai", methods=["POST"])
def save_ai_settings():
    """Save or update AI configuration."""
    api_key = request.form.get("api_key", "").strip()
    api_base_url = request.form.get("api_base_url", "").strip()
    model_name = request.form.get("model_name", "").strip()

    if not api_key:
        flash("API Key 不能为空", "danger")
        return redirect(url_for("settings.settings_page"))

    if not api_base_url:
        api_base_url = "https://api.deepseek.com"
    if not model_name:
        model_name = "deepseek-chat"

    settings = AISettings.query.first()
    if not settings:
        settings = AISettings()
        db.session.add(settings)

    settings.api_key = api_key
    settings.api_base_url = api_base_url
    settings.model_name = model_name
    settings.updated_at = datetime.utcnow()

    db.session.commit()
    flash("✅ AI 配置已保存", "success")
    return redirect(url_for("settings.settings_page"))
