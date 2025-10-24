from flask import Flask, render_template_string, request, redirect
from python_modules.db_connector import DB

app = Flask(__name__)
db = DB("db/events.db")

# HTML Template (Bootstrap for nice layout)
TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Linux Security Guardian - Dashboard</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background-color: #0e1111; color: #ddd; }
    table { background-color: #1c1f1f; }
    .critical { color: #ff4c4c; }
    .warning { color: #f1c232; }
    .info { color: #5cb85c; }
    h1 { color: #7fd1ff; }
  </style>
</head>
<body>
<div class="container mt-4">
  <h1 class="text-center mb-4">Linux Security Guardian Dashboard</h1>
  <form method="GET" action="/">
    <div class="input-group mb-3">
      <input type="text" name="search" class="form-control" placeholder="Search event details..." value="{{search}}">
      <button class="btn btn-primary">Search</button>
      <a href="/" class="btn btn-secondary">Reset</a>
    </div>
  </form>
  <table class="table table-striped table-hover table-bordered">
    <thead>
      <tr>
        <th>Timestamp</th>
        <th>Event Type</th>
        <th>Details</th>
      </tr>
    </thead>
    <tbody>
    {% for e in events %}
      <tr>
        <td>{{e[1]}}</td>
        <td><b>{{e[2]}}</b></td>
        <td>{{e[3]}}</td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
  <p class="text-muted text-center">Showing {{ events|length }} events.</p>
</div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    search = request.args.get("search", "")
    all_events = db.fetch_events()
    if search:
        all_events = [e for e in all_events if search.lower() in e[3].lower()]
    return render_template_string(TEMPLATE, events=all_events, search=search)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

