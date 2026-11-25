# OWASP ZAP Verification and Comparison

- **Tool:** OWASP ZAP 2.17.0, daemon mode, API bound to `127.0.0.1:8090`, fresh local session, local-only API key (not committed).
- **Scope enforcement:** only the explicit URLs `http://127.0.0.1:5000` and, in a separate phase, `http://127.0.0.1:5001` were spidered and actively scanned. No public or third-party target was touched.
- **Method:** spider (6 URLs vulnerable, 5 URLs secure), passive scan drained to 0 records, then active scan completed on each target. Alert counts below are the actual `core/view/alerts` output filtered by target URL; no de-duplication was applied.
- **Raw export:** `dast/zap-alerts-sanitized.json` and `dast/zap-alerts-sanitized.csv` (alert name, risk, confidence, URL, parameter and short evidence only).

| Observation | Vulnerable (5000) | Secure (5001) | Interpretation |
|---|---|---|---|
| Alerts (total) | 22 | 16 | Both apps scanned with the same spider + active scan policy |
| High risk | 4 | 0 | All High alerts were XSS on the vulnerable app |
| XSS alerts | 4 (3 DOM-based High/High confidence; 1 reflected High/Medium confidence) | 0 | Validation and auto-escaping removed XSS findings |
| CSP header not set | 6 | 5 | Present on both - not addressed by this experiment |
| Missing anti-clickjacking header | 3 | 3 | Present on both - not addressed by this experiment |
| Server version disclosure | 6 | 5 | Present on both - Flask/Werkzeug default header |
| X-Content-Type-Options missing | 3 | 3 | Present on both - not addressed by this experiment |


## Notable XSS alerts recorded on the vulnerable app
| Alert | Risk | Confidence | Parameter | Evidence |
|---|---|---|---|---|
| Cross Site Scripting (DOM Based) | High | High | (fragment) | Browser-driven payload written into form inputs on `/` |
| Cross Site Scripting (DOM Based) | High | High | `name` | Browser-driven `<script>alert(5397)</script>` on `/result` |
| Cross Site Scripting (Reflected) | High | Medium | `name` | `</div><scrIpt>alert(1);</scRipt><div>` |

These are ZAP-generated payloads and are separate from the manual proof-of-execution payload in the report. The secure phase produced **no XSS alerts**.

## Limitations
ZAP active scanning is automated and its confidence values are the tool's own ratings; the reflected XSS finding was independently confirmed by the manual browser test and alert text. Header-related alerts remain open in both versions because adding response headers was outside the validation scope. ZAP's `includeInScope`/`clearScope` core actions were unavailable in this 2.17 build, so scope was enforced by scanning only the two explicit localhost target URLs.
