#!/bin/bash

# Security Scanning Script for PackOptima
# Runs multiple security tools to identify vulnerabilities

set -e

echo "========================================="
echo "PackOptima Security Scan"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create reports directory
mkdir -p security_reports

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Bandit - Python security linter
echo "========================================="
echo "1. Running Bandit (Python Security Linter)"
echo "========================================="
if command_exists bandit; then
    bandit -r ../app -f json -o security_reports/bandit_report.json || true
    bandit -r ../app -f txt -o security_reports/bandit_report.txt || true
    echo -e "${GREEN}✓ Bandit scan complete${NC}"
    echo "Report: security_reports/bandit_report.txt"
else
    echo -e "${YELLOW}⚠ Bandit not installed. Install with: pip install bandit${NC}"
fi
echo ""

# 2. Safety - Check dependencies for known vulnerabilities
echo "========================================="
echo "2. Running Safety (Dependency Vulnerability Check)"
echo "========================================="
if command_exists safety; then
    safety check --json --output security_reports/safety_report.json || true
    safety check --output security_reports/safety_report.txt || true
    echo -e "${GREEN}✓ Safety scan complete${NC}"
    echo "Report: security_reports/safety_report.txt"
else
    echo -e "${YELLOW}⚠ Safety not installed. Install with: pip install safety${NC}"
fi
echo ""

# 3. pip-audit - Audit Python packages for known vulnerabilities
echo "========================================="
echo "3. Running pip-audit"
echo "========================================="
if command_exists pip-audit; then
    pip-audit --format json --output security_reports/pip_audit_report.json || true
    pip-audit --output security_reports/pip_audit_report.txt || true
    echo -e "${GREEN}✓ pip-audit scan complete${NC}"
    echo "Report: security_reports/pip_audit_report.txt"
else
    echo -e "${YELLOW}⚠ pip-audit not installed. Install with: pip install pip-audit${NC}"
fi
echo ""

# 4. Semgrep - Static analysis for security patterns
echo "========================================="
echo "4. Running Semgrep (Static Analysis)"
echo "========================================="
if command_exists semgrep; then
    semgrep --config=auto --json --output=security_reports/semgrep_report.json ../app || true
    semgrep --config=auto --output=security_reports/semgrep_report.txt ../app || true
    echo -e "${GREEN}✓ Semgrep scan complete${NC}"
    echo "Report: security_reports/semgrep_report.txt"
else
    echo -e "${YELLOW}⚠ Semgrep not installed. Install with: pip install semgrep${NC}"
fi
echo ""

# 5. Check for secrets in code
echo "========================================="
echo "5. Checking for Secrets in Code"
echo "========================================="
if command_exists detect-secrets; then
    detect-secrets scan ../app > security_reports/secrets_report.json || true
    echo -e "${GREEN}✓ Secrets scan complete${NC}"
    echo "Report: security_reports/secrets_report.json"
else
    echo -e "${YELLOW}⚠ detect-secrets not installed. Install with: pip install detect-secrets${NC}"
fi
echo ""

# 6. Check requirements.txt for outdated packages
echo "========================================="
echo "6. Checking for Outdated Packages"
echo "========================================="
pip list --outdated > security_reports/outdated_packages.txt || true
echo -e "${GREEN}✓ Outdated packages check complete${NC}"
echo "Report: security_reports/outdated_packages.txt"
echo ""

# 7. Run security tests
echo "========================================="
echo "7. Running Security Tests"
echo "========================================="
if command_exists pytest; then
    pytest test_multi_tenant_isolation.py -v -m security --tb=short > security_reports/security_tests.txt 2>&1 || true
    echo -e "${GREEN}✓ Security tests complete${NC}"
    echo "Report: security_reports/security_tests.txt"
else
    echo -e "${YELLOW}⚠ pytest not installed${NC}"
fi
echo ""

# 8. Check for common security misconfigurations
echo "========================================="
echo "8. Checking for Security Misconfigurations"
echo "========================================="
echo "Checking for common issues..." > security_reports/misconfigurations.txt

# Check for DEBUG=True in production
if grep -r "DEBUG.*=.*True" ../app/*.py 2>/dev/null; then
    echo "⚠ WARNING: DEBUG=True found in code" >> security_reports/misconfigurations.txt
fi

# Check for hardcoded secrets
if grep -r "password.*=.*['\"]" ../app/*.py 2>/dev/null | grep -v "password_hash" | grep -v "# "; then
    echo "⚠ WARNING: Potential hardcoded passwords found" >> security_reports/misconfigurations.txt
fi

# Check for SQL string concatenation
if grep -r "execute.*%.*" ../app/*.py 2>/dev/null; then
    echo "⚠ WARNING: Potential SQL injection vulnerability (string formatting in execute)" >> security_reports/misconfigurations.txt
fi

echo -e "${GREEN}✓ Misconfiguration check complete${NC}"
echo "Report: security_reports/misconfigurations.txt"
echo ""

# 9. Generate summary report
echo "========================================="
echo "9. Generating Summary Report"
echo "========================================="

cat > security_reports/SUMMARY.md << 'EOF'
# Security Scan Summary

## Scan Date
EOF

date >> security_reports/SUMMARY.md

cat >> security_reports/SUMMARY.md << 'EOF'

## Tools Used
- Bandit (Python security linter)
- Safety (dependency vulnerability checker)
- pip-audit (package vulnerability audit)
- Semgrep (static analysis)
- detect-secrets (secrets detection)
- Custom security tests

## Critical Findings

### High Priority
- Review bandit_report.txt for HIGH severity issues
- Review safety_report.txt for known vulnerabilities
- Review pip_audit_report.txt for vulnerable packages

### Medium Priority
- Review semgrep_report.txt for security patterns
- Review secrets_report.json for exposed secrets
- Review misconfigurations.txt for common issues

### Low Priority
- Review outdated_packages.txt for updates
- Review security_tests.txt for test failures

## Remediation Steps

1. **Fix Critical Vulnerabilities**
   - Update vulnerable dependencies
   - Remove hardcoded secrets
   - Fix SQL injection vulnerabilities

2. **Address Medium Issues**
   - Review and fix Bandit warnings
   - Implement missing security controls
   - Update security configurations

3. **Improve Security Posture**
   - Update outdated packages
   - Add missing security tests
   - Implement security best practices

## Next Steps

1. Review all reports in security_reports/ directory
2. Prioritize fixes based on severity
3. Create tickets for remediation
4. Re-run scan after fixes
5. Schedule regular security scans

## Compliance Checklist

- [ ] Zero critical vulnerabilities
- [ ] All dependencies up to date
- [ ] No secrets in code
- [ ] Multi-tenant isolation verified
- [ ] Input validation implemented
- [ ] API keys encrypted at rest
- [ ] TLS 1.2+ enforced
- [ ] Rate limiting implemented
- [ ] Security tests passing

EOF

echo -e "${GREEN}✓ Summary report generated${NC}"
echo "Report: security_reports/SUMMARY.md"
echo ""

# 10. Display summary
echo "========================================="
echo "Security Scan Complete"
echo "========================================="
echo ""
echo "Reports generated in: security_reports/"
echo ""
echo "Key reports:"
echo "  - SUMMARY.md (overview)"
echo "  - bandit_report.txt (Python security issues)"
echo "  - safety_report.txt (vulnerable dependencies)"
echo "  - semgrep_report.txt (security patterns)"
echo ""
echo "Next steps:"
echo "  1. Review SUMMARY.md"
echo "  2. Address critical findings"
echo "  3. Run security tests: pytest -m security"
echo "  4. Re-scan after fixes"
echo ""

# Check for critical issues
CRITICAL_FOUND=0

if [ -f security_reports/bandit_report.json ]; then
    HIGH_ISSUES=$(grep -c '"issue_severity": "HIGH"' security_reports/bandit_report.json || echo "0")
    if [ "$HIGH_ISSUES" -gt 0 ]; then
        echo -e "${RED}⚠ Found $HIGH_ISSUES HIGH severity issues in Bandit scan${NC}"
        CRITICAL_FOUND=1
    fi
fi

if [ -f security_reports/safety_report.json ]; then
    VULNERABILITIES=$(grep -c '"vulnerability"' security_reports/safety_report.json || echo "0")
    if [ "$VULNERABILITIES" -gt 0 ]; then
        echo -e "${RED}⚠ Found $VULNERABILITIES vulnerable dependencies${NC}"
        CRITICAL_FOUND=1
    fi
fi

if [ $CRITICAL_FOUND -eq 1 ]; then
    echo ""
    echo -e "${RED}CRITICAL ISSUES FOUND - Review reports immediately${NC}"
    exit 1
else
    echo -e "${GREEN}No critical issues found${NC}"
    exit 0
fi
