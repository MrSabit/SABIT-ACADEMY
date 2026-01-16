# Email Configuration Setup

To use the password reset functionality, you need to configure email settings. Set the following environment variables:

## Development Mode (No Email Configuration Required)

The system now works out of the box without email configuration! When email is not set up:

1. The system will automatically enter development mode
2. Password reset links will be displayed in the console/log
3. Users will see a message: "Email is not configured. Check the console for the reset link."

This allows you to test the password reset functionality immediately without any email setup.

## Production Email Configuration

For production use, configure email with these environment variables:

### Gmail Configuration (Recommended)

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"

3. Set environment variables:
```bash
set MAIL_SERVER=smtp.gmail.com
set MAIL_PORT=587
set MAIL_USE_TLS=true
set MAIL_USERNAME=your-email@gmail.com
set MAIL_PASSWORD=your-app-password
set MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### Alternative SMTP Services

You can also use other SMTP providers like:
- Outlook: smtp-mail.outlook.com
- Yahoo: smtp.mail.yahoo.com
- SendGrid, Mailgun, etc.

## Testing

### Development Testing (No Email Setup)
1. Go to login page
2. Click "Forgot your password?"
3. Enter your email address
4. Check the console/log for the reset link
5. Copy/paste the link into your browser
6. Reset your password

### Production Testing (With Email)
1. Configure email settings above
2. Go to login page
3. Click "Forgot your password?"
4. Enter your email address
5. Check your email for reset link
6. Click the link and reset your password

## Security Notes

- In development mode, reset links are visible in console logs
- In production, email should be properly configured
- Reset tokens expire after 1 hour for security
- Invalid tokens are properly rejected
