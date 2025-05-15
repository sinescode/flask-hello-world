import smtplib
import socket
import dns.resolver
import time

INVALID_MAILBOX_STATUS = [450, 550, 553]
VALID_MAILBOX_STATUS = [250, 251]

def get_mx_for_domain(domain="gmail.com"):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        mx_records = sorted((r.preference, str(r.exchange).rstrip('.')) for r in answers)
        return mx_records[0][1] if mx_records else None
    except Exception as e:
        print(f"Error fetching MX for {domain}: {e}")
        return None

def check_email_availability(email, mx_host):
    try:
        with smtplib.SMTP(mx_host, port=25, timeout=3) as smtp:
            smtp.ehlo()
            smtp.mail('asadulhoqk@gmail.com')
            code, response = smtp.rcpt(email)
            
            if code in VALID_MAILBOX_STATUS:
                return False
            elif code in INVALID_MAILBOX_STATUS:
                return True
            return None
    except (smtplib.SMTPException, socket.timeout, ConnectionRefusedError, socket.gaierror) as e:
        print(f"SMTP error checking {email}: {e}")
        return None

def check_email_availability_with_retry(email, mx_host, max_retries=2, delay=2):
    for attempt in range(max_retries):
        result = check_email_availability(email, mx_host)
        if result is not None:
            return result
        
        if attempt < max_retries - 1:
            print(f"Retrying {email} in {delay} seconds...")
            time.sleep(delay)
    
    print(f"Giving up on {email} after {max_retries} attempts")
    return None