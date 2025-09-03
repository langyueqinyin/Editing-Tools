from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def portal():
    return render_template("index.html", version="2025-09-02-03")

@app.route("/timecode")
def timecode():
    return render_template("timecode.html", version="2025-09-02-03")

if __name__ == "__main__":
    # for local dev only
    app.run(debug=True)