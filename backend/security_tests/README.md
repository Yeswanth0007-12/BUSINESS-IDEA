# Security Testing for PackOptima

This directory contains security tests and scanning tools for PackOptima.

## Security Testing Tools

### 1. Multi-Tenant Isolation Tests
Tests to ensure data isolation between companies.

```bash
pytest test_multi_tenant_isolation.py -v -m security
```

### 2. Security Scanning Script
Automated security scanning using multiple tools.

```bash
# On Linux/Mac
chmod +x run_security_scan.sh
./run_security_scan.sh

# On Windows
bash run_security_scan.sh
```

## Required Tools

Install security scanning tools:

```bash
# Python security tools
pip install bandit safety pip-audit semgrep detect-secrets

# Or install all at once
pip install bandit safety pip-audit semgrep detect-secrets pytest
```

## Security Scan Components

### 1. Bandit
Python security linter that finds common security issues.

**Checks for**:
- SQL injection vulnerabilities
- Hardcoded passwords
- Use of insecure functions
- Weak cryptography

### 2. Safety
Checks Python dependencies for known security vulnerabilities.

**Checks for**:
- Known CVEs in dependencies
- Vulnerable package versions
- Security advisories

### 3. pip-audit
Audits Python packages for known vulnerabilities.

**Checks for**:
- Package vulnerabilities
- Dependency conflicts
- Security patches

### 4. Semgrep
Static analysis tool for finding security patterns.

**Checks for**:
- Security anti-patterns
- Common vulnerabilities
- Best practice violations

### 5. detect-secrets
Finds secrets accidentally committed to code.

**Checks for**:
- API keys
- Passwords
- Tokens
- Private keys

## Security Requirements

### Critical Requirements (Must Pass)

1. **Zero Critical Vulnerabilities**
   - No HIGH severity issues in Bandit
   - No known CVEs in dependencies
   - No secrets in code

2. **Multi-Tenant Isolation**
   - Users cannot access other company's data
   - All queries filtered by company_id
   - API keys are company-specific

3. **Input Validation**
   - All inputs validated using Pydantic
   - SQL injection prevented
   - XSS prevented
   - Command injection prevented

4. **Data Encryption**
   - API keys hashed with SHA-256
   - Webhook secrets encrypted at rest
   - Passwords hashed with bcrypt
   - TLS 1.2+ for all external communications

5. **Authentication & Authorization**
   - JWT tokens with expiration
   - API key constant-time comparison
   - Rate limiting enforced
   - Failed login rate limiting

## Running Security Tests

### Run All Security Tests
```bash
pytest test_multi_tenant_isolation.py -v -m security
```

### Run Specific Test Classes
```bash
# Multi-tenant isolation
pytest test_multi_tenant_isolation.py::TestMultiTenantIsolation -v

# Input validation
pytest test_multi_tenant_isolation.py::TestInputValidation -v

# Authentication security
pytest test_multi_tenant_isolation.py::TestAuthenticationSecurity -v

# Data encryption
pytest test_multi_tenant_isolation.py::TestDataEncryption -v

# Rate limiting
pytest test_multi_tenant_isolation.py::TestRateLimiting -v
```

## Security Scan Reports

After running `run_security_scan.sh`, reports are generated in `security_reports/`:

- **SUMMARY.md**: Overview of all findings
- **bandit_report.txt**: Python security issues
- **safety_report.txt**: Vulnerable dependencies
- **pip_audit_report.txt**: Package vulnerabilities
- **semgrep_report.txt**: Security patterns
- **secrets_report.json**: Potential secrets
- **misconfigurations.txt**: Common security issues
- **outdated_packages.txt**: Packages needing updates
- **security_tests.txt**: Test results

## Remediation Workflow

### 1. Review Reports
```bash
# View summary
cat security_reports/SUMMARY.md

# View critical issues
cat security_reports/bandit_report.txt | grep "HIGH"
cat security_reports/safety_report.txt
```

### 2. Fix Critical Issues
Priority order:
1. Known CVEs in dependencies (update packages)
2. HIGH severity Bandit issues
3. Secrets in code (remove and rotate)
4. SQL injection vulnerabilities
5. Authentication issues

### 3. Update Dependencies
```bash
# Update vulnerable packages
pip install --upgrade <package_name>

# Update all packages (carefully)
pip install --upgrade -r requirements.txt
```

### 4. Re-run Scans
```bash
./run_security_scan.sh
```

### 5. Verify Fixes
```bash
pytest test_multi_tenant_isolation.py -v -m security
```

## Common Security Issues and Fixes

### SQL Injection
**Issue**: String concatenation in SQL queries
```python
# BAD
query = f"SELECT * FROM products WHERE id = {product_id}"

# GOOD
query = "SELECT * FROM products WHERE id = :id"
db.execute(query, {"id": product_id})
```

### Hardcoded Secrets
**Issue**: Secrets in code
```python
# BAD
API_KEY = "sk_live_12345"

# GOOD
API_KEY = os.getenv("API_KEY")
```

### Weak Password Hashing
**Issue**: Using MD5 or SHA for passwords
```python
# BAD
password_hash = hashlib.md5(password.encode()).hexdigest()

# GOOD
from passlib.hash import bcrypt
password_hash = bcrypt.hash(password)
```

### Missing Input Validation
**Issue**: No validation on user input
```python
# BAD
def create_product(name: str):
    # No validation

# GOOD
from pydantic import BaseModel, validator

class ProductCreate(BaseModel):
    name: str
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v
```

## Security Checklist

Before deployment, verify:

- [ ] Security scan passes with zero critical issues
- [ ] All security tests pass
- [ ] No secrets in code
- [ ] All dependencies up to date
- [ ] Multi-tenant isolation verified
- [ ] Input validation implemented
- [ ] API keys encrypted at rest
- [ ] Webhook secrets encrypted
- [ ] TLS 1.2+ enforced
- [ ] Rate limiting configured
- [ ] Failed login rate limiting enabled
- [ ] CORS configured correctly
- [ ] Security headers set
- [ ] Logging excludes sensitive data

## Continuous Security

### Schedule Regular Scans
```bash
# Add to crontab for weekly scans
0 2 * * 0 cd /path/to/backend/security_tests && ./run_security_scan.sh
```

### Pre-commit Hooks
Add security checks to pre-commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-r', 'app']
  
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
```

### CI/CD Integration
Add to GitHub Actions:

```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install bandit safety pip-audit
      - name: Run security scan
        run: |
          cd backend/security_tests
          ./run_security_scan.sh
```

## Contact

For security issues, contact: security@packoptima.com

**Do not** create public issues for security vulnerabilities.
