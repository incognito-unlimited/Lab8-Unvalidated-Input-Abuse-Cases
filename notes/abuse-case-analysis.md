# Abuse Case Analysis - Lab 8 Experiment 15

All observations below were produced locally on `127.0.0.1` on 200 / 200 responses; no third-party system was tested.

## Abuse Case 1 - Script injection through unescaped output

- **Input field:** Name
- **Exact payload:** `<script>alert('Lab 8 XSS demo')</script>` (quantity `1`)
- **HTTP response (vulnerable):** status `200`, 944 bytes, 43.0 ms. The raw response body contained the exact `<script>` tag (`raw_script_present = True`), i.e. no HTML encoding was applied.
- **Browser behaviour:** a JavaScript alert appeared; Selenium read its text as `'Lab 8 XSS demo'`. After accepting it, the result page contained `1` `<script>` element inside `#rendered-name`, with DOM innerHTML `"<script>alert('Lab 8 XSS demo')</script>"`.
- **Conclusion:** this is **confirmed script execution**, not merely reflected text. Screenshots `02-xss-payload-submitted.png` and `03-xss-result.png` are genuine captures; the alert text was recorded by the browser driver because native dialogs are not part of a page screenshot.
- **Root cause:** the template uses `{{ name|safe }}`, which explicitly disables Jinja auto-escaping for untrusted input.
- **Demonstrated impact:** attacker-controlled JavaScript runs in the page origin in the test browser.
- **Potential impact (not demonstrated here):** reading page-accessible data, performing actions as the user, or phishing - actual impact depends on page data, session cookie flags and any CSP.
- **Mitigation:** remove `|safe`; rely on contextual output encoding (Jinja auto-escaping for HTML text), validate input against an allowlist, add a Content-Security-Policy as defence in depth.

## Abuse Case 2 - Negative quantity / business-logic abuse

- **Input field:** Quantity
- **Exact payload:** `-5` (name `Aditey`)
- **HTTP response (vulnerable):** status `200`, 920 bytes; displayed quantity `-5`, calculated total `-500`. No exception or rejection occurred.
- **Browser behaviour:** the result page rendered the negative total and applied the `negative` CSS class to it; genuine screenshots `04-negative-quantity-submitted.png` and `05-negative-quantity-result.png`.
- **Conclusion:** the negative quantity was accepted into the calculation and a negative total was displayed.
- **Root cause:** the application converts the raw value with `int()` and multiplies without checking sign, type constraints or business limits.
- **Demonstrated impact:** an invalid order total is displayed by the application.
- **Potential impact (not demonstrated here):** incorrect order totals, inventory inconsistency, invalid transaction records and abuse of downstream logic that trusts the total. No financial exploitation is claimed because no payment or fulfilment flow exists in this demo.
- **Mitigation:** strict integer parsing, `quantity > 0`, a maximum such as 100, and enforcement in the business/service layer rather than only in the browser.

## Optional Abuse Case - Excessively long input

- **Input:** a 5000-character string of `A` in the Name field.
- **HTTP response:** status `200`, 5904 bytes, 6.04 ms. The browser rendered all `5000` characters without an error; total remained `100`.
- **Conclusion:** there is no field length limit. This is **not** a buffer overflow: Python strings are heap-managed and no memory-corruption condition or crash was observed. The screenshot `06-overlong-input-test.png` is a genuine capture.
- **Potential impact:** excessive storage/rendering cost or downstream failures if such input is persisted or processed elsewhere.
- **Mitigation:** enforce request and field size limits and bounded processing.

## Distinctions
- **Demonstrated:** alert execution, raw unsanitised `<script>` in the response, `-5` accepted with total `-500`, 5,000-character name accepted.
- **Potential:** data theft, inventory corruption, denial of service - plausible consequences, not measured outcomes.
- **Assumptions:** testing used a local, disposable Flask process and synthetic values only.
- **Limitations:** no authenticated session, payment flow or persistent storage was present; native alert text was captured via the WebDriver API rather than visible inside the page screenshot.
