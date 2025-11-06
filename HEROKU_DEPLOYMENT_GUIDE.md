# 🚀 Heroku Deployment Guide for Data Cloud App

This guide will help you deploy your Data Cloud Management Application to Heroku.

---

## 📋 Prerequisites

1. **Heroku Account**
   - Sign up at: https://signup.heroku.com/

2. **Heroku CLI**
   - Install from: https://devcenter.heroku.com/articles/heroku-cli
   - Verify installation: `heroku --version`

3. **Git**
   - Already initialized in your project
   - Verify: `git --version`

---

## 📁 Files Created for Heroku Deployment

✅ **Procfile** - Tells Heroku how to run your app
```
web: gunicorn app:app
```

✅ **requirements.txt** - Python dependencies
```
Flask==3.0.0
Flask-CORS==4.0.0
simple-salesforce==1.12.6
gunicorn==21.2.0
requests==2.31.0
Werkzeug==3.0.1
```

✅ **runtime.txt** - Specifies Python version
```
python-3.11.7
```

✅ **.gitignore** - Excludes unnecessary files from deployment

---

## 🚀 Deployment Steps

### Step 1: Initialize Git Repository (if not already done)

```bash
cd "/Users/bbanerjee/.cursor/DC MCP/datacloud_app"
git init
git add .
git commit -m "Initial commit - Data Cloud App ready for Heroku"
```

### Step 2: Login to Heroku

```bash
heroku login
```

This will open your browser for authentication.

### Step 3: Create Heroku App

```bash
# Create app with auto-generated name
heroku create

# OR create with custom name
heroku create your-datacloud-app-name
```

Note: Heroku app names must be unique across all Heroku apps globally.

### Step 4: Set Environment Variables (if using Salesforce credentials)

```bash
# Set Salesforce credentials as environment variables
heroku config:set SF_USERNAME="your-salesforce-username"
heroku config:set SF_PASSWORD="your-salesforce-password"
heroku config:set SF_SECURITY_TOKEN="your-security-token"

# Or if using connected app
heroku config:set SF_CONSUMER_KEY="your-consumer-key"
heroku config:set SF_CONSUMER_SECRET="your-consumer-secret"
```

### Step 5: Deploy to Heroku

```bash
git push heroku main
```

Or if your branch is named `master`:
```bash
git push heroku master
```

### Step 6: Scale the Web Dyno

```bash
heroku ps:scale web=1
```

### Step 7: Open Your App

```bash
heroku open
```

Or visit: `https://your-app-name.herokuapp.com`

---

## 🔧 Important Configuration Changes

### 1. Update Session Secret Key

In `app.py`, change the secret key to use environment variable:

```python
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
```

Then set it on Heroku:
```bash
heroku config:set SECRET_KEY="$(openssl rand -hex 32)"
```

### 2. Update CORS Configuration (if needed)

In `app.py`, update allowed origins for production:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-app-name.herokuapp.com"],
        "supports_credentials": True
    }
})
```

### 3. Data Persistence

⚠️ **IMPORTANT:** Heroku's filesystem is ephemeral!

Your current data files (`data/*.json`, `data/*.csv`) will be lost on dyno restart.

**Solutions:**

**Option A: Use Heroku Postgres** (Recommended for production)
```bash
heroku addons:create heroku-postgresql:mini
```

**Option B: Use AWS S3 for file storage**
- Store JSON/CSV files in S3
- Update file reading/writing logic

**Option C: Keep files (for testing only)**
- Files will persist during the session
- Will reset when dyno restarts (every 24 hours)
- Good for demos, not for production

---

## 📊 View Logs

```bash
# View real-time logs
heroku logs --tail

# View specific number of lines
heroku logs -n 200
```

---

## 🔄 Update Your App

After making changes:

```bash
git add .
git commit -m "Description of changes"
git push heroku main
```

---

## 🛠️ Useful Heroku Commands

```bash
# Check app status
heroku ps

# Restart all dynos
heroku restart

# Run bash on Heroku
heroku run bash

# Check environment variables
heroku config

# Set environment variable
heroku config:set KEY=VALUE

# Remove environment variable
heroku config:unset KEY

# View app info
heroku apps:info

# Scale dynos
heroku ps:scale web=1

# Open app in browser
heroku open
```

---

## 💰 Pricing

- **Free Tier (Eco Dynos):** $5/month for 1000 dyno hours
- **Hobby:** $7/month per dyno
- **Professional:** $25-$500/month

**Note:** Heroku removed the free tier in November 2022. The cheapest option is Eco dynos at $5/month.

---

## 🐛 Troubleshooting

### App Crashes

1. Check logs:
   ```bash
   heroku logs --tail
   ```

2. Common issues:
   - Missing dependencies in `requirements.txt`
   - Port binding issues (use `os.environ.get('PORT', 5001)`)
   - File path issues (use absolute paths)

### Port Configuration

Update `app.py` to use Heroku's PORT:

```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### Database Connection Issues

- Check environment variables: `heroku config`
- Verify Salesforce credentials
- Check CORS settings

---

## 🔒 Security Best Practices

1. ✅ Never commit credentials to Git
2. ✅ Use environment variables for all secrets
3. ✅ Set `DEBUG=False` in production
4. ✅ Use HTTPS only
5. ✅ Implement rate limiting
6. ✅ Sanitize user inputs
7. ✅ Use strong session secrets

---

## 📱 Alternative Deployment Options

If you don't want to use Heroku:

1. **AWS Elastic Beanstalk**
   - More control, similar pricing
   - Better for long-term production

2. **Google Cloud Run**
   - Serverless, pay-per-use
   - Good for variable traffic

3. **DigitalOcean App Platform**
   - Simple deployment
   - $5/month starter tier

4. **Railway.app**
   - Modern alternative to Heroku
   - Free tier available

5. **Render.com**
   - Free tier with limitations
   - Easy deployment from GitHub

---

## ✅ Post-Deployment Checklist

- [ ] App is accessible via Heroku URL
- [ ] Login functionality works
- [ ] Salesforce connection successful
- [ ] All dashboards load correctly
- [ ] AI Agent responds properly
- [ ] Segment creation works
- [ ] Email generation functions
- [ ] Data persists (if using database)
- [ ] Environment variables set correctly
- [ ] HTTPS enabled (automatic on Heroku)
- [ ] Custom domain configured (optional)

---

## 📞 Support

- **Heroku Dev Center:** https://devcenter.heroku.com/
- **Heroku Status:** https://status.heroku.com/
- **Support:** https://help.heroku.com/

---

## 🎉 Success!

Once deployed, your app will be accessible at:
**https://your-app-name.herokuapp.com**

Share the URL with your team and start using your Data Cloud Management Application in production! 🚀


