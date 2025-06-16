# 🚀 Programmatic Deployment Guide

Since Streamlit Cloud doesn't support CLI/API deployment, here are **alternative platforms** that support programmatic deployment for your SF State Scraper web app.

## 🚫 Streamlit Cloud Limitation

**Important:** Streamlit Cloud requires manual deployment through their web interface. There is no CLI or API for programmatic deployment.

## ✅ Programmatic Alternatives

### 1. 🔧 **One-Click Deployment Script**

Use our Python deployment script that supports multiple platforms:

```bash
# Deploy to Heroku
python deploy.py heroku

# Deploy to Railway  
python deploy.py railway

# Deploy to Render
python deploy.py render

# Deploy to all platforms
python deploy.py all
```

### 2. 🚀 **Heroku** (Recommended)

**Quick Deploy:**
```bash
# Run the Heroku deployment script
./deploy_heroku.sh
```

**Manual Steps:**
```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login and create app
heroku login
heroku create your-app-name

# Add Chrome buildpacks for Selenium
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-google-chrome.git
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-chromedriver.git

# Deploy
git push heroku main
```

**Pros:** ✅ Full CLI support, ✅ Great Selenium support, ✅ Free tier available  
**Cons:** ❌ Limited free hours

### 3. 🚂 **Railway**

**Quick Deploy:**
```bash
# Run the Railway deployment script
./deploy_railway.sh
```

**Manual Steps:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**Pros:** ✅ Modern CLI, ✅ Good free tier, ✅ Auto-scaling  
**Cons:** ❌ Newer platform (less mature)

### 4. 🎨 **Render**

Uses Git-based deployment with `render.yaml` configuration:

```bash
# Push to GitHub, then connect to Render
git push origin main
```

**Pros:** ✅ Git-based deployment, ✅ Free tier, ✅ SSL included  
**Cons:** ❌ Slower cold starts

### 5. ☁️ **Google Cloud Run** (Advanced)

For advanced users who want maximum control:

```bash
# Build and deploy with Cloud Build
gcloud builds submit --tag gcr.io/PROJECT-ID/sf-state-scraper
gcloud run deploy --image gcr.io/PROJECT-ID/sf-state-scraper --platform managed
```

## 🔄 CI/CD Automation

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Heroku
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: akhileshns/heroku-deploy@v3.12.12
      with:
        heroku_api_key: ${{secrets.HEROKU_API_KEY}}
        heroku_app_name: "your-app-name"
        heroku_email: "your-email@example.com"
```

## 📊 Platform Comparison

| Platform | Cost | CLI | Selenium Support | Cold Start |
|----------|------|-----|------------------|------------|
| **Heroku** | Free tier + paid | ✅ Excellent | ✅ Great | ~30s |
| **Railway** | Free tier + paid | ✅ Good | ✅ Good | ~10s |
| **Render** | Free tier + paid | ⚠️ Git-based | ✅ Good | ~60s |
| **Streamlit Cloud** | Free | ❌ Web only | ⚠️ Limited | ~30s |

## 🎯 Recommended Approach

1. **For quick deployment:** Use Heroku with our script
2. **For modern workflow:** Use Railway 
3. **For Git-based deployment:** Use Render
4. **For manual deployment:** Use Streamlit Cloud (web interface)

## 🔧 Environment Variables

All platforms support environment variables for sensitive data:

```bash
# Heroku
heroku config:set API_KEY=your_secret_key

# Railway  
railway variables set API_KEY=your_secret_key

# Render (in dashboard or render.yaml)
envVars:
  - key: API_KEY
    value: your_secret_key
```

## 🚀 Quick Start

1. **Choose a platform** from the options above
2. **Run the deployment script:**
   ```bash
   python deploy.py heroku --app-name my-scraper
   ```
3. **Your web app will be live** in 3-5 minutes!

## 🆘 Troubleshooting

**Chrome Driver Issues:**
- Ensure buildpacks are added in correct order
- Check that `packages.txt` includes Chrome dependencies

**Memory Errors:**
- Upgrade to paid tier for more RAM
- Optimize your scraping code

**Deployment Failures:**
- Check build logs for specific errors
- Verify `requirements.txt` dependencies

---

**Bottom Line:** While Streamlit Cloud is great for simplicity, these alternatives give you the programmatic deployment control you need! 🎯 