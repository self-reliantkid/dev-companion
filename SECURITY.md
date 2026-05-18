# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.1.x   | :white_check_mark: |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take the security of dev-companion seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do Not Disclose Publicly

Please do not create a public GitHub issue for security vulnerabilities. This helps protect users while we work on a fix.

### 2. Report Privately

Send details to: **security@dev-companion.dev** (or create a private security advisory on GitHub)

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### 3. Response Timeline

- **Initial Response:** Within 48 hours
- **Status Update:** Within 7 days
- **Fix Timeline:** Depends on severity
  - Critical: 1-7 days
  - High: 7-14 days
  - Medium: 14-30 days
  - Low: 30-90 days

### 4. Disclosure Process

1. We confirm the vulnerability
2. We develop and test a fix
3. We release a security patch
4. We publicly disclose the vulnerability (with credit to reporter, if desired)

## Security Best Practices

### For Users

1. **Protect API Keys:**
   - Never commit `.env` files to version control
   - Use environment variables for credentials
   - Rotate keys regularly

2. **Keep Dependencies Updated:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Review Generated Code:**
   - Always review AI-generated code before using in production
   - Test thoroughly in a safe environment
   - Be cautious with code that handles sensitive data

4. **Limit Permissions:**
   - Use read-only GitHub tokens when possible
   - Restrict watsonx.ai API key permissions
   - Follow principle of least privilege

### For Contributors

1. **Code Review:**
   - All code changes require review
   - Security-sensitive changes need extra scrutiny
   - Use static analysis tools

2. **Dependencies:**
   - Keep dependencies minimal
   - Audit new dependencies before adding
   - Monitor for known vulnerabilities

3. **Input Validation:**
   - Validate all user inputs
   - Sanitize code before processing
   - Prevent injection attacks

4. **Secrets Management:**
   - Never hardcode credentials
   - Use `.env` files (excluded from git)
   - Document required environment variables

## Known Security Considerations

### API Key Exposure

**Risk:** API keys in `.env` files could be accidentally committed.

**Mitigation:**
- `.env` is in `.gitignore`
- `.bobignore` blocks Bob from accessing secrets
- Documentation emphasizes key protection

### Code Injection

**Risk:** Malicious code in user input could be executed.

**Mitigation:**
- Code is analyzed, not executed
- Sandboxed processing
- Input validation and sanitization

### Dependency Vulnerabilities

**Risk:** Third-party packages may have vulnerabilities.

**Mitigation:**
- Minimal dependency footprint
- Regular dependency updates
- Automated vulnerability scanning (planned)

### AI Model Risks

**Risk:** AI-generated code may contain vulnerabilities.

**Mitigation:**
- Clear warnings in documentation
- Encourage code review
- Validation and testing of outputs

## Security Features

### Current

- ✅ Environment variable-based credential management
- ✅ `.gitignore` for sensitive files
- ✅ `.bobignore` for Bob IDE protection
- ✅ Input validation in API client
- ✅ Token caching with secure storage

### Planned

- ⏳ Automated dependency vulnerability scanning
- ⏳ Code signing for releases
- ⏳ Security audit logging
- ⏳ Rate limiting for API calls
- ⏳ Encrypted credential storage

## Compliance

### Data Privacy

- **No Data Collection:** We don't collect or store user data
- **API Usage:** Code is sent to IBM watsonx.ai per their terms
- **GitHub Access:** Only with explicit user authorization

### License Compliance

- MIT License allows commercial use
- Dependencies are MIT/Apache 2.0 compatible
- No GPL or restrictive licenses

## Security Contacts

- **Primary:** security@dev-companion.dev
- **GitHub:** Create a private security advisory
- **Maintainer:** @self-reliantkid

## Acknowledgments

We appreciate security researchers who responsibly disclose vulnerabilities. Contributors will be:
- Credited in security advisories (if desired)
- Listed in SECURITY_CONTRIBUTORS.md
- Thanked in release notes

---

**Last Updated:** 2026-05-18  
**Version:** 2.1.0