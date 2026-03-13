import dns.resolver
import re
from fastapi import HTTPException

# Known disposable email providers to block
DISPOSABLE_DOMAINS = {
    "mailinator.com",
    "yopmail.com",
    "tempmail.com",
    "guerrillamail.com",
    "10minutemail.com",
    "temp-mail.org",
}

def validate_email_domain(email: str) -> bool:
    """
    VALIDATION POLICY:
    1. Check for valid email format.
    2. Reject known disposable email domains to ensure user data quality.
    3. Try resolving MX records to verify domain capability (optional).
    4. Allow anything else to support custom/company domains.
    """
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise HTTPException(status_code=400, detail="enter a valid domain")

    domain = email.split('@')[-1].lower()

    if domain in DISPOSABLE_DOMAINS:
        raise HTTPException(status_code=400, detail="Disposable email domains are not allowed")

    # Try optional MX record resolution to check if domain exists and can receive emails
    try:
        records = dns.resolver.resolve(domain, 'MX')
        if not records:
            pass
    except Exception:
        # Don't strictly block if DNS fails or is misconfigured
        pass

    return True
