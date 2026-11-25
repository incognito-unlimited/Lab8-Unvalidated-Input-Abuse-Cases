"""
DELIBERATELY INSECURE - LOCAL LAB DEMONSTRATION ONLY.

This Flask application intentionally accepts untrusted input without
server-side validation and renders it as trusted HTML. It is bound to
127.0.0.1 and Flask debug mode is disabled. Do not deploy or expose it.
"""

from flask import Flask, request, render_template_string

app = Flask(__name__)

FORM_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Lab 8 - Deliberately Unvalidated Demo (LOCAL ONLY)</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 32px; color: #222; }
    .warning { background: #fee2e2; border: 1px solid #991b1b; padding: 12px; }
    label { display: block; margin: 18px 0 6px; font-weight: bold; }
    input { width: 460px; padding: 8px; font-size: 15px; }
    button { padding: 9px 18px; font-size: 15px; cursor: pointer; }
    code { background: #f3f4f6; padding: 2px 5px; }
  </style>
</head>
<body>
  <div class="warning">
    <strong>DELIBERATELY INSECURE DEMO - LOCALHOST ONLY.</strong>
    This form performs no server-side validation and treats submitted HTML as trusted.
  </div>
  <h2>Demo order form - vulnerable version</h2>
  <form action="/result" method="get">
    <label for="name">Name</label>
    <input id="name" name="name" value="{{ name }}">

    <label for="quantity">Quantity</label>
    <input id="quantity" name="quantity" value="{{ quantity }}">

    <p><button type="submit">Submit order</button></p>
  </form>
  <p>Suggested local payloads:
    <code>&lt;script&gt;alert('Lab 8 XSS demo')&lt;/script&gt;</code> and
    <code>-5</code>.
  </p>
  <p><a href="/">Clear form</a></p>
</body>
</html>
"""

RESULT_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Lab 8 - Vulnerable Result (LOCAL ONLY)</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 32px; color: #222; }
    .card { border: 1px solid #d1d5db; padding: 18px; max-width: 760px; }
    .negative { color: #b91c1c; font-weight: bold; }
    .warning { background: #fee2e2; border: 1px solid #991b1b; padding: 12px; }
  </style>
</head>
<body>
  <div class="warning"><strong>DELIBERATELY INSECURE RESULT - LOCALHOST ONLY.</strong></div>
  <h2>Submitted order - vulnerable version</h2>
  <div class="card">
    <p><strong>Name as rendered:</strong></p>
    <div id="rendered-name">{{ name|safe }}</div>
    <p><strong>Quantity:</strong> <span id="quantity">{{ quantity }}</span></p>
    <p><strong>Calculated total:</strong>
       <span id="total" class="{{ 'negative' if total is number and total < 0 else '' }}">{{ total }}</span>
    </p>
  </div>
  <p><a href="/">Back to form</a></p>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    # No validation or sanitisation: values are reflected straight back into the form.
    name = request.args.get("name", "")
    quantity = request.args.get("quantity", "")
    return render_template_string(FORM_TEMPLATE, name=name, quantity=quantity)


@app.route("/result", methods=["GET", "POST"])
def result():
    # Intentionally unsafe: no length, character, type, sign or range checks.
    name = request.values.get("name", "")
    quantity_raw = request.values.get("quantity", "")

    try:
        quantity = int(quantity_raw)
    except (TypeError, ValueError):
        # Still no validation: keep the raw value and avoid a server exception.
        quantity = quantity_raw

    if isinstance(quantity, int):
        total = quantity * 100
    else:
        total = "Not calculable (non-numeric quantity)"

    # The safe filter deliberately bypasses Jinja auto-escaping.
    return render_template_string(
        RESULT_TEMPLATE,
        name=name,
        quantity=quantity_raw,
        total=total,
    )


if __name__ == "__main__":
    # Local-only binding; debug mode is intentionally disabled.
    app.run(host="127.0.0.1", port=5000, debug=False)
