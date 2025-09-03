from flask import Blueprint, render_template

bp = Blueprint(
    "timecode", __name__,
    template_folder="../../templates",  # 继续用根模板
    static_folder="static"             # 让 /timecode/static/* 生效
)

@bp.get("/")
def page():
    return render_template("timecode.html", version="2025-09-03-06")
