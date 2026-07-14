"""
Unique World Robotics — School Outreach Mail Merge
====================================================
Sends a personalized email (with the UWR brochure attached) to every school
in UWR_School_Outreach_List.csv that has a usable email address.

HOW TO USE
----------
1. Put this script, UWR_School_Outreach_List.csv, and the brochure PDF in the
   same folder.
2. Fill in the SENDER SETTINGS below (email + app password).
   - For a Google Workspace / Gmail address, generate an "App Password":
     Google Account -> Security -> 2-Step Verification -> App passwords.
     Do NOT use your normal login password.
   - For Microsoft 365 / Outlook, use smtp.office365.com, port 587, and your
     normal password (or an app password if MFA is enforced).
3. Do a DRY RUN first (default) — it prints what would be sent without
   sending anything. Check the output carefully.
4. Set DRY_RUN = False to actually send.
5. Run:  python3 send_school_outreach.py

The script tracks progress in sent_log.csv so you can safely re-run it —
already-sent schools are skipped automatically.
"""

import csv
import smtplib
import ssl
import time
import os
from email.message import EmailMessage

# ============ SENDER SETTINGS — EDIT THESE ============
SENDER_EMAIL = "your email"
SENDER_PASSWORD = "password"   # never commit this to git / share this file publicly
SMTP_SERVER = "smtp.gmail.com"      # use "smtp.office365.com" if this is a Microsoft/Outlook mailbox
SMTP_PORT = 587
SENDER_NAME = "Anshul Raj"
SENDER_TITLE = "Business Development Executive, Unique World Robotics"
REPLY_TO = "anshulrajsv0@gmail.com"
PHONE = "+91 7025571985"

# ============ CAMPAIGN SETTINGS ============
CSV_FILE = "UWR_School_Outreach_List.csv"
BROCHURE_FILE = "Unique_World_Robotics_Updated_Brochure_.pdf"
LOG_FILE = "sent_log.csv"
DRY_RUN = False        # <-- set to False only after you've reviewed a dry run
DELAY_SECONDS = 8       # pause between sends to avoid spam-filtering / rate limits

SUBJECT_TEMPLATE = "Partnering with {school} — STEM & Robotics Programs by Unique World Robotics"

BODY_TEMPLATE = """Dear Sir/Madam,

I hope this email finds you well.

My name is {sender_name}, and I'm reaching out from Unique World Robotics
(UWR) — a STEM.org accredited robotics and technology education company
headquartered in Dubai, with 20+ innovation centers across India and the
UAE. We've had the privilege of working with schools such as GEMS
Education, Mar Thoma Central School, RVS Group, and Amal Jyothi College of
Engineering, and have trained student teams that have gone on to win at
WRO Nationals and Internationals.

I'm writing to introduce our programs to {school} and explore how we
could partner to bring hands-on STEM education to your students —
through robotics labs, certified upskilling courses, competition training
(WRO, FLL, FTC, FIRST Global), and teacher/master-class training.

I've attached our brochure with more details on our programs and track
record. I'd love to schedule a short call or an in-person visit to walk
you through how we could design a program suited to {school}'s students.

Please let me know a convenient time, or feel free to reach me directly
at {phone}.

Looking forward to the opportunity to work together.

Warm regards,
{sender_name}
{sender_title}
Unique World Robotics | www.uwrindia.com
{phone}
"""


def load_already_sent():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, newline="", encoding="utf-8") as f:
        return {row["School Name"] for row in csv.DictReader(f)}


def log_sent(school, email, status):
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["School Name", "Email", "Status", "Timestamp"])
        writer.writerow([school, email, status, time.strftime("%Y-%m-%d %H:%M:%S")])


def build_message(school, to_email):
    msg = EmailMessage()
    msg["Subject"] = SUBJECT_TEMPLATE.format(school=school)
    msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg["To"] = to_email
    msg["Reply-To"] = REPLY_TO
    body = BODY_TEMPLATE.format(
        sender_name=SENDER_NAME,
        sender_title=SENDER_TITLE,
        school=school,
        phone=PHONE,
    )
    msg.set_content(body)

    with open(BROCHURE_FILE, "rb") as f:
        data = f.read()
    msg.add_attachment(
        data,
        maintype="application",
        subtype="pdf",
        filename="Unique_World_Robotics_Brochure.pdf",
    )
    return msg


def main():
    already_sent = load_already_sent()

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    targets = [r for r in rows if r["Primary Email"].strip() and r["Status"] == "Ready"]
    skipped_no_email = [r for r in rows if not r["Primary Email"].strip() or r["Status"] != "Ready"]

    print(f"Total schools in list: {len(rows)}")
    print(f"Schools with usable email: {len(targets)}")
    print(f"Schools skipped (no email / needs lookup): {len(skipped_no_email)}")
    print(f"Already sent previously (per {LOG_FILE}): {len(already_sent)}")
    print(f"Mode: {'DRY RUN (nothing will be sent)' if DRY_RUN else 'LIVE SEND'}")
    print("-" * 60)

    if not DRY_RUN:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls(context=ssl.create_default_context())
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

    sent_count = 0
    for row in targets:
        school = row["School Name"]
        to_email = row["Primary Email"].strip()

        if school in already_sent:
            print(f"SKIP (already sent): {school}")
            continue

        msg = build_message(school, to_email)

        if DRY_RUN:
            print(f"[DRY RUN] Would send to: {school} <{to_email}>")
            print(f"   Subject: {msg['Subject']}")
        else:
            try:
                server.send_message(msg)
                print(f"SENT: {school} <{to_email}>")
                log_sent(school, to_email, "SENT")
                sent_count += 1
                time.sleep(DELAY_SECONDS)
            except Exception as e:
                print(f"FAILED: {school} <{to_email}> — {e}")
                log_sent(school, to_email, f"FAILED: {e}")

    if not DRY_RUN:
        server.quit()
        print("-" * 60)
        print(f"Done. Successfully sent {sent_count} new emails this run.")

    if skipped_no_email:
        print("-" * 60)
        print("Schools needing manual email lookup:")
        for r in skipped_no_email:
            print(f"  - {r['School Name']}")


if __name__ == "__main__":
    main()
