School Outreach Mail Merge
A local, zero-API-cost tool for running personalized cold/warm email outreach campaigns at scale — built for sending targeted emails (with an attached brochure) to a list of schools, without paying per-email costs or relying on a third-party AI service to send the mail.
Why this exists
Cold outreach campaigns naturally have low response rates. Running every email through a paid AI API adds cost for no real benefit when the bottleneck isn't email quality — it's getting a clean, validated list and reliably delivering to it. This script handles the whole pipeline locally in Python: validate the data, personalize the message, attach the brochure, send with rate limiting, and log everything so the campaign can be safely resumed.
Features
✅ Reads a CSV of schools and filters to only records with a usable email and a `Ready` status
✅ Automatically skips schools with missing emails or incomplete records, and prints them out for manual follow-up
✅ Personalizes subject line and body per school using a template
✅ Attaches a PDF brochure to every email
✅ Dry Run mode — preview exactly what would be sent, to whom, with what subject line, before anything goes out
✅ Rate-limits sends (configurable delay) to avoid tripping spam filters
✅ Logs every send attempt (success or failure) to `sent_log.csv`, so re-running the script skips schools that were already emailed — safe to resume after an interruption without duplicate sends
Requirements
Python 3.8+
No external dependencies — uses only the Python standard library (`csv`, `smtplib`, `ssl`, `email`, `os`, `time`)
Setup
Clone this repo and place the following in the same folder as the script:
Your contact list as `UWR_School_Outreach_List.csv`
Your brochure as a PDF
Set your sender credentials as environment variables (never hardcode them):
```bash
   export SENDER_EMAIL="you@example.com"
   export SENDER_PASSWORD="your-app-password"
   export SENDER_NAME="Your Name"
   export SENDER_TITLE="Your Title, Your Company"
   export PHONE="+1 555 555 5555"
   ```
For Gmail / Google Workspace, generate an App Password (Google Account → Security → 2-Step Verification → App Passwords). Do not use your normal account password.
For Microsoft 365 / Outlook, set `SMTP_SERVER` to `smtp.office365.com` and use your regular password (or an app password if MFA is enforced).
Your CSV needs at minimum these columns:
Column	Description
`School Name`	Used for personalization and logging
`Primary Email`	The recipient address
`Status`	Must equal `Ready` for the row to be included in the send
Usage
Always dry-run first. With `DRY_RUN = True` (the default), the script prints exactly what it would send without sending anything:
```bash
python3 send_school_outreach.py
```
Review the output carefully. Once you're confident, set `DRY_RUN = False` in the script and run it again to send for real.
```bash
python3 send_school_outreach.py
```
If the run is interrupted, just run it again — schools already logged in `sent_log.csv` are skipped automatically, so nothing gets emailed twice.
![Dry run output](screenshots/Screenshot 2026-07-14 174511.png)
Output
Console output: a live summary of what's being sent, skipped, or has already been sent, plus a final list of schools that need manual email lookup.
`sent_log.csv`: a running log of every send attempt with timestamp and status, used to make re-runs idempotent.
Security notes
Never commit real credentials, CSVs of personal contact data, or `sent_log.csv` to a public repository. Add them to `.gitignore`.
Use environment variables or a `.env` file (not committed) for all sender settings.
If you ever accidentally commit an app password, revoke it immediately in your email provider's security settings and generate a new one — deleting the commit alone doesn't invalidate it if it was ever pushed.
License
MIT (or your preference — add a `LICENSE` file before publishing).
