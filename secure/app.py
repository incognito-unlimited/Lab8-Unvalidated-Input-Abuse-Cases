"""
SECURE whitelist-validation counterpart for Lab 8.

This version performs all validation on the server using explicit allowlists
and boundaries. It never treats submitted text as trusted HTML and relies on
normal Jinja auto-escaping. Bound to 127.0.0.1:5001 with debug disabled.
"""

import re

from flask import Flask, request, render_template_string

app = Flask(__name__)

# Allowlist rules (server-side only).
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z '-]{1,49}$")  # 2-50 characters
MAX_QUANTITY_RAW_LENGTH = 10  # prevents needlessly large integer conversion
MAX_QUANTITY = 100

FORM_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Lab 8 - Secure Whitelist Validation (LOCAL ONLY)</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 32px; color: #222; }
    .ok { background: #dcfce7; border: 1px solid #166534; padding: 12px; }
    .error { background: #fee2e2; border: 1px solid #991b1b; padding: 12px; }
    label { display: block; margin: 18px 0 6px; font-weight: bold; }
    input { width: 460px; padding: 8px; font-size: 15px; }
    button { padding: 9px 18px; font-size: 15px; cursor: pointer; }
    code { background: #f3f4f6; padding: 2px 5px; }
    li { margin: 5px 0; }
  </style>
</head>
<body>
  <div class="ok"><strong>SECURE VERSION - server-side whitelist validation - LOCALHOST ONLY.</strong></div>
  <h2>Demo order form - secure version</h2>
  {% if errors %}
  <div class="error">
    <strong>Input rejected by server-side validation:</strong>
    <ul>{% for error in errors %}<li>{{ error }}</li>{% endfor %}</ul>
  </div>
  {% endif %}
  <form action="/result" method="get">
    <label for="name">Name (2-50 letters, spaces, apostrophes, hyphens)</label>
    <input id="name" name="name" value="{{ name }}">

    <label for="quantity">Quantity (integer 1-100)</label>
    <input id="quantity" name="quantity" value="{{ quantity }}">

    <p><button type="submit">Submit order</button></p>
  </form>
  <p>Submitted values above are shown with normal template auto-escaping.</p>
  <p><a href="/">Clear form</a></p>
</body>
</html>
"""

RESULT_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Lab 8 - Secure Result (LOCAL ONLY)</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 32px; color: #222; }
    .card { border: 1px solid #d1d5db; padding: 18px; max-width: 760px; }
    .ok { background: #dcfce7; border: 1px solid #166534; padding: 12px; }
  </style>
</head>
<body>
  <div class="ok"><strong>SECURE VERSION - valid input accepted after server-side validation.</strong></div>
  <h2>Submitted order - secure version</h2>
  <div class="card">
    <p><strong>Name:</strong> <span id="rendered-name">{{ name }}</span></p>
    <p><strong>Quantity:</strong> <span id="quantity">{{ quantity }}</span></p>
    <p><strong>Calculated total:</strong> <span id="total">{{ total }}</span></p>
  </div>
  <p>The name is rendered with normal auto-escaping, so markup is displayed as text, not executed.</p>
  <p><a href="/">Back to form</a></p>
</body>
</html>
"""


def validate(name_raw, quantity_raw):
    """Return (errors, name, quantity). All checks occur on the server."""
    errors = []

    name = name_raw if isinstance(name_raw, str) else ""
    if not name:
        errors.append("Name is required.")
    elif not NAME_PATTERN.fullmatch(name):
        errors.append(
            "Name must be 2-50 characters: start with a letter and use only "
            "letters, spaces, apostrophes or hyphens. HTML tags and unexpected "
            "characters are rejected."
        )

    quantity_text = quantity_raw if isinstance(quantity_raw, str) else ""
    quantity = None
    if not quantity_text:
        errors.append("Quantity is required.")
    elif len(quantity_text) > MAX_QUANTITY_RAW_LENGTH:
        errors.append("Quantity is too long; enter an integer from 1 to 100.")
    elif not re.fullmatch(r"[0-9]+", quantity_text):
        errors.append(
            "Quantity must be a whole number from 1 to 100; negative values, "
            "zero, decimals and non-numeric input are rejected."
        )
    else:
        quantity = int(quantity_text)
        if quantity < 1:
            errors.append("Quantity must be greater than zero.")
        elif quantity > MAX_QUANTITY:
            errors.append("Quantity must not exceed 100.")
        else:
            quantity = quantity  # validated integer

    return errors, name, quantity_text, quantity


@app.route("/", methods=["GET"])
def index():
    return render_template_string(
        FORM_TEMPLATE, name="", quantity="", errors=[]
    )


@app.route("/result", methods=["GET", "POST"])
def result():
    name_raw = request.values.get("name", "")
    quantity_raw = request.values.get("quantity", "")
    errors, name, quantity_text, quantity = validate(name_raw, quantity_raw)

    if errors:
        # Reflect the rejected values only through auto-escaped template output.
        return render_template_string(
            FORM_TEMPLATE, name=name, quantity=quantity_text, errors=errors
        ), 400

    # Safe path: values have passed the allowlists; output is still auto-escaped.
    return render_template_string(
        RESULT_TEMPLATE,
        name=name,
        quantity=quantity_text,
        total=quantity * 100,
    )


if __name__ == "__main__":
    # Local-only binding; debug mode is disabled.
    app.run(host="127.0.0.1", port=5001, debug=False)
