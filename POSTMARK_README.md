# Postmark Email Integration
 
We have successfully switched the Django email backend from SendGrid to Postmark using Postmark's SMTP service.

## 1. What was changed?
- Replaced the SendGrid SMTP server details with Postmark's SMTP details.
- Postmark requires the `POSTMARK_SERVER_TOKEN` to be used for both the SMTP Username (`EMAIL_HOST_USER`) and the SMTP Password (`EMAIL_HOST_PASSWORD`).

## 2. Where are the changes?
The following files were updated:

### `config/settings/base.py`
Old configuration:
```python
# Email Settings (SendGrid)
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.getenv('SENDGRID_API_KEY')
```

**New configuration:**
```python
# Email Settings (Postmark)
EMAIL_HOST = 'smtp.postmarkapp.com'
EMAIL_HOST_USER = os.getenv('POSTMARK_SERVER_TOKEN')
EMAIL_HOST_PASSWORD = os.getenv('POSTMARK_SERVER_TOKEN')
```

### `.env` and `.env.example`
The environment variable name was changed to match the new service.
- Deleted: `SENDGRID_API_KEY`
- Added: `POSTMARK_SERVER_TOKEN`

## 3. Next Steps for You
1. Log in to your [Postmark account](https://postmarkapp.com/).
2. Go to your active **Server** (or create one).
3. Click on the **API Tokens** tab.
4. Copy the Server API Token.
5. Open your `.env` file and set the value:
   ```env
   POSTMARK_SERVER_TOKEN=your_copied_long_token-string-here
   ```
6. Ensure your sender signature (the `DEFAULT_FROM_EMAIL` value) is verified in the Postmark dashboard. Otherwise, emails will throw an error.
