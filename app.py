from flask import Flask, render_template
import importlib, json, pathlib

app = Flask(__name__)

def discover_tools():
    base = pathlib.Path(__file__).parent / "tools"
    cards = []
    if not base.exists():
        return cards
    for pkg in sorted([p for p in base.iterdir() if p.is_dir()]):
        manifest_path = pkg / "manifest.json"
        if not manifest_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("hidden"):
            continue
        slug = manifest.get("slug", pkg.name)
        entry = manifest.get("entry", "web:bp")
        title = manifest.get("name", slug.title())
        desc = manifest.get("desc", "")
        order = manifest.get("order", 100)

        mod_name, attr = entry.split(":")
        module = importlib.import_module(f"tools.{pkg.name}.{mod_name}")
        bp = getattr(module, attr)
        app.register_blueprint(bp, url_prefix=f"/{slug}")

        cards.append({"slug": slug, "title": title, "desc": desc, "path": f"/{slug}", "order": order})
    cards.sort(key=lambda x: x.get("order", 100))
    return cards

TOOL_CARDS = discover_tools()

@app.route("/")
def portal():
    return render_template("index.html", tools=TOOL_CARDS, version="2025-09-03-02")

if __name__ == "__main__":
    app.run(debug=True)