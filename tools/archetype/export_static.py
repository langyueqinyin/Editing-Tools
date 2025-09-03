# export_static.py —— 生成 dist/index.html（纯静态可交互页面）
from pathlib import Path
from jinja2 import Template  # pip install jinja2
import json

# 复用 app.py 里的数据加载和模板
from app import load_data, TPL

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "dist"
OUT_DIR.mkdir(exist_ok=True)

from app import load_data, TPL
positions, works, notes = load_data()
html = Template(TPL).render(
    positions=json.dumps(positions, ensure_ascii=False),
    works=json.dumps(works, ensure_ascii=False),
    notes=json.dumps(notes, ensure_ascii=False),   # NEW
)

out_file = OUT_DIR / "index.html"
out_file.write_text(html, encoding="utf-8")
print("✅ 已生成:", out_file)
