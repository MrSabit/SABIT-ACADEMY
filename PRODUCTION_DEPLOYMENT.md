# Production Deployment Guide for Render

## 🚀 Email Configuration for Production

### Step 1: Choose Email Service

**SendGrid (Recommended)**
- Free tier: 100 emails/day
- Better deliverability
- Professional setup

**Gmail (Good for small apps)**
- Free but limited
- Requires App Password
- Good for testing/small projects

### Step 2: Configure Environment Variables in Render

Go to your Render service → Environment → Add Environment Variables:

#### SendGrid Configuration:
```
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=apikey
MAIL_PASSWORD=sg.xxxxx.xxxxx.xxxxx (your SendGrid API key)
MAIL_DEFAULT_SENDER=your-email@yourdomain.com
```

#### Gmail Configuration:
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=xxxx-xxxx-xxxx (your Gmail App Password)
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### Step 3: Get SendGrid Setup (if using SendGrid)

1. **Create SendGrid Account**: https://sendgrid.com
2. **Generate API Key**:
   - Settings → API Keys → Create API Key
   - Select "Full Access" or "Restricted Access" with mail.send enabled
   - Copy the API key (starts with "SG.")
3. **Verify Sender**:
   - Settings → Sender Authentication
   - Verify your domain or single sender
   - Required for production use

### Step 4: Get Gmail App Password (if using Gmail)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Google Account → Security → 2-Step Verification → App passwords
   - Select "Mail" and your device
   - Copy the 16-character password
3. **Use App Password** in MAIL_PASSWORD (not your regular password)

### Step 5: Deploy to Render

1. **Push changes to Git**
2. **Render will auto-deploy**
3. **Test password reset** with a real email

### Step 6: Verify Production Setup

After deployment:
1. Go to your app on Render
2. Try "Forgot Password" with your email
3. Check your email inbox (and spam folder)
4. Test the reset link

## 🔧 PostgreSQL Configuration

Your app is already configured to use PostgreSQL in production via the `DATABASE_URL` environment variable that Render provides automatically.

## 🛡️ Security Notes

- **Never commit email credentials to Git**
- **Use environment variables only**
- **Monitor email usage** (SendGrid limits)
- **Set up SPF/DKIM records** for better deliverability
- **Test thoroughly** before going live

## 📊 Monitoring

Check your Render logs for:
- Email sending errors
- Password reset requests
- Database connection issues

## 🆘 Troubleshooting

**Email not sending?**
- Verify environment variables are set
- Check Render logs for errors
- Ensure API key is valid (SendGrid)
- Confirm App Password is correct (Gmail)

**Reset link not working?**
- Check SERVER_NAME is set correctly
- Verify HTTPS is being used
- Check token expiration (1 hour)

**Database issues?**
- Ensure PostgreSQL is running
- Check DATABASE_URL format
- Run migrations if needed
