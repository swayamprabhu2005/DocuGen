# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Yes     |

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

Please email `security@docugen.example.com` with:

1. A description of the vulnerability
2. Steps to reproduce
3. Affected versions
4. Proposed fix (if any)

We will respond within **72 hours** and aim to release a patch within **14 days** of confirmation.

## Scope

Security issues that are in-scope:
- Remote code execution via crafted input data
- Path traversal in custom template loading
- Jinja2 sandbox bypass in template rendering
- Denial of service from malformed documents

Out of scope:
- Issues requiring physical access to the user's machine
- Social engineering attacks

## Local-First Security Notes

DocuGen AI is designed to run entirely locally. It:
- Makes **no network requests** by default
- Does **not** send document data to any external service
- Uses a **Jinja2 SandboxedEnvironment** for template rendering to prevent code injection

If you use the optional `[ml]` or `[nlp]` extras, those packages may make network requests on first model download.
