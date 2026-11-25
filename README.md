# Lab 8 - Unvalidated Input Program and Abuse Case Demonstration

**Student:** Aditey Mehra | **Roll:** 2301730266 | B.Tech CSE (AI & ML), Section D, Semester 7 | K.R. Mangalam University
**Subject:** Secure Coding and Vulnerabilities | **Lab 8, Experiment 15**

## Aim
Develop a deliberately unvalidated Flask application, demonstrate two concrete abuse cases (script injection and a negative quantity), implement a separate secure whitelist-validation counterpart, document genuine evidence, and analyse the security consequences of accepting untrusted input without validation.

## LOCAL-ONLY SAFETY WARNING
The `vulnerable/` application is **deliberately insecure** and must only be run on `127.0.0.1`. It performs no server-side validation and renders submitted HTML as trusted. Both applications bind to localhost and have Flask debug mode disabled. Do not expose either app to a shared network or deploy it publicly. All data used is synthetic.

## Installation and execution
```powershell
python -m pip install -r requirements.txt

# Terminal 1 - deliberately vulnerable demo (port 5000)
python vulnerable/app.py

# Terminal 2 - secure whitelist-validation counterpart (port 5001)
python secure/app.py
```
Open `http://127.0.0.1:5000/` and `http://127.0.0.1:5001/` in a browser.

## Application design
Both programs accept a **Name** and a **Quantity** and calculate `total = quantity * 100`.
The vulnerable version reflects `name` through `{ name|safe }` (bypassing Jinja auto-escaping), converts quantity with a bare `int()` and has no length, character, sign or range checks. The secure version validates everything on the server with `^[A-Za-z][A-Za-z '-]{1,49}$` for the name and an integer range of 1-100 for quantity, then renders with normal auto-escaping.

## Abuse-case reproduction
1. **Script injection / XSS:** at `http://127.0.0.1:5000/`, put `<script>alert('Lab 8 XSS demo')</script>` in **Name**, `1` in **Quantity**, and submit. Result recorded: HTTP 200; a JavaScript alert with text `Lab 8 XSS demo` executed; one `<script>` element was present in the rendered DOM.
2. **Negative quantity:** submit `Aditey` and `-5`. Result recorded: HTTP 200; displayed quantity `-5`; calculated total `-500`.
3. **Long input (optional):** submitted a 5,000-character name. Result recorded: HTTP 200; all 5,000 characters rendered; no error and no buffer overflow.

## Secure whitelist-validation comparison
The same payloads were sent to `http://127.0.0.1:5001/result`:
- Script-injection name: **HTTP 400**, explicit rejection message, markup shown as inert escaped text.
- Quantity `-5`: **HTTP 400**, explicit rejection message.
- Ordinary input (`Aditey Mehra`, `3`): **HTTP 200**, name `Aditey Mehra`, quantity `3`, total `300`.

See `notes/validation-test-results.md` for the full matrix and `notes/zap-comparison.md` for scanner observations.

## Test results summary
| Test | Vulnerable | Secure |
|---|---|---|
| Script injection | XSS executed (alert text `Lab 8 XSS demo`) | Rejected with HTTP 400; no script rendered |
| Negative quantity | `-5` accepted; total `-500` | Rejected with HTTP 400 |
| 5,000-character name | HTTP 200; 5,000 characters rendered | Rejected with HTTP 400 by length/allowlist rule |

## Security analysis
Root causes in the vulnerable version are unsafe output rendering (`|safe`), missing type/sign/range validation and missing length limits. Demonstrated consequences are script execution in the page origin and an invalid negative order total. Potential (not demonstrated here) consequences include session/data exposure through XSS and corrupt totals, inventory records or downstream business logic through negative quantities. Mitigations are context-aware output encoding, removal of `|safe`, strict server-side parsing with allowlists and bounds, request/field size limits and a CSP as defence in depth.

OWASP ZAP 2.17.0 scanned only the two localhost targets: the vulnerable app produced 22 alerts including 4 High-risk XSS alerts (3 DOM-based High confidence, 1 reflected Medium confidence); the secure app produced 16 alerts and **no XSS alerts**. Both apps still showed missing CSP, missing anti-clickjacking header, server version disclosure and missing X-Content-Type-Options - these are header hardening issues outside this experiment's validation scope.

## Repository contents
- `vulnerable/app.py` - intentionally insecure demonstration app (port 5000).
- `secure/app.py` - server-side whitelist-validation counterpart (port 5001).
- `evidence/` - nine genuine browser screenshots taken during the local test run.
- `notes/` - abuse-case analysis, validation results and ZAP comparison.
- `dast/` - sanitised ZAP alert export.
- `report/` - editable DOCX and exported PDF.

No credentials, tokens, personal data or unrelated secrets are committed.
