# tools/archetype/web.py — FIX: JSON-dump data for TPL that expects {{ positions | safe }}
from flask import Blueprint, render_template_string
import json
from .app import load_data, TPL

bp = Blueprint("archetype", __name__)

@bp.get("/")
def page():
    positions, works, notes = load_data()
    # The TPL (in app.py) embeds variables like: POSITIONS = {{ positions | safe }}
    # It expects JSON strings, not Python objects — so we dump to JSON here.
    return render_template_string(
        TPL,
        positions=json.dumps(positions, ensure_ascii=False),
        works=json.dumps(works, ensure_ascii=False),
        notes=json.dumps(notes, ensure_ascii=False),
    )