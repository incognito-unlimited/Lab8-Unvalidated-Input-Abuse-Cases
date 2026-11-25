# Secure Whitelist Validation - Test Results

Secure app: `http://127.0.0.1:5001`, separate process, `debug=False`, localhost-only binding.
Rules: Name must match `^[A-Za-z][A-Za-z '-]{1,49}$`; Quantity must be an integer string of at most 10 digits with value 1-100. All checks run on the server; the browser performs no validation.

| Test | Vulnerable version (actual) | Secure version (actual) | Control demonstrated |
|---|---|---|---|
| XSS payload in Name | HTTP 200; raw `<script>` in body; alert executed | HTTP 400; rejected; escaped text only | Output encoding + allowlist validation |
| Negative quantity -5 | HTTP 200; quantity -5; total -500 | HTTP 400; rejected | Server-side sign/range validation |
| Long name (5,000 chars) | HTTP 200; 5,000 chars rendered | HTTP 400; rejected by length/allowlist | Length/request size limits |
| Zero quantity | Not separately tested | HTTP 400 by quantity >= 1 rule | Range validation |
| Decimal quantity | Not separately tested | HTTP 400 by integer-only regex | Strict integer parsing |
| Ordinary input | HTTP 200 (name reflected) | HTTP 200; name `Aditey Mehra`; qty 3; total 300 | Valid input accepted safely |


## Exact observed messages (secure version)
- Script-injection name -> `Input rejected by server-side validation:
Name must be 2-50 characters: start with a letter and use only letters, spaces, apostrophes or hyphens. HTML tags and unexpected characters are rejected.`
- Quantity `-5` -> `Input rejected by server-side validation:
Quantity must be a whole number from 1 to 100; negative values, zero, decimals and non-numeric input are rejected.`
- Valid input -> name `Aditey Mehra`, quantity `3`, total `300`.

The secure error page re-displays the rejected values only through auto-escaped template output, so the script-injection payload appears as inert escaped text and does not execute. The secure version does not add security headers; that is a separate hardening task noted in `notes/zap-comparison.md`.
