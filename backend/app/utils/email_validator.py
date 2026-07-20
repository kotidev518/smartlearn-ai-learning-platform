import dns.resolver
import re
from fastapi import HTTPException

<<<<<<< HEAD
# Common public providers that are globally trusted
PUBLIC_PROVIDER_ALLOWLIST = {
    "gmail.com",
    "outlook.com",
    "hotmail.com",
    "live.com",
    "yahoo.com",
    "icloud.com",
    "me.com",
    "proton.me",
    "protonmail.com",
    "aol.com",
}

=======
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
# Known disposable email providers to block
DISPOSABLE_DOMAINS = {
    "mailinator.com",
    "yopmail.com",
    "tempmail.com",
    "guerrillamail.com",
    "10minutemail.com",
    "temp-mail.org",
}

<<<<<<< HEAD
# Trusted Top-Level Domains (Academic/Institutional/Government)
TRUSTED_TLDS = {
    "edu", "gov", "ac.in", "ac.uk", "org", "edu.in", "mil", "int"
}

# Explicitly allowed custom organization domains (if needed)
KNOWN_ORGANIZATIONS = {
    "microsoft.com", "google.com", "apple.com", "meta.com", "amazon.com"
}

def validate_email_domain(email: str) -> bool:
    """
    STRICT VALIDATION POLICY:
    1. Public Providers (Gmail, etc.) are ALWAYS allowed.
    2. Educational, Governmental, and Trusted TLDs are ALLOWED.
    3. Explicitly whitelisted organizations are ALLOWED.
    4. Everything else is REJECTED to ensure high quality user data.
=======
def validate_email_domain(email: str) -> bool:
    """
    VALIDATION POLICY:
    1. Check for valid email format.
    2. Reject known disposable email domains to ensure user data quality.
    3. Try resolving MX records to verify domain capability (optional).
    4. Allow anything else to support custom/company domains.
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
    """
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise HTTPException(status_code=400, detail="enter a valid domain")

    domain = email.split('@')[-1].lower()

<<<<<<< HEAD
    # 1. Trusted Public Providers
    if domain in PUBLIC_PROVIDER_ALLOWLIST:
        return True

    # 2. Block Known Disposables first
    if domain in DISPOSABLE_DOMAINS:
        raise HTTPException(status_code=400, detail="enter a valid domain")

    # 3. Check Known Organizations Whitelist
    if domain in KNOWN_ORGANIZATIONS:
        return True

    # 4. Check for Trusted TLDs (e.g. .edu, .ac.in)
    # This ensures we allow academic institutions by default.
    if any(domain.endswith(f".{tld}") for tldld in TRUSTED_TLDS for tld in [tldld]):
        # Even for trusted TLDs, we check MX records for existence
        try:
            records = dns.resolver.resolve(domain, 'MX')
            if records:
                return True
        except:
            pass

    # 5. NEW STRICT RULE: Reject any other custom domain (like ex3.com)
    raise HTTPException(status_code=400, detail="enter a valid domain")
=======
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
>>>>>>> 7eeaba13be676b85039c9769cd6fde229373c5bd
