#!/bin/bash

# Heroku Programmatic Deployment Script
echo "🚀 Starting Heroku deployment..."

# Install Heroku CLI if not present
if ! command -v heroku &> /dev/null; then
    echo "Installing Heroku CLI..."
    curl https://cli-assets.heroku.com/install.sh | sh
fi

# Login to Heroku (requires API key)
heroku auth:token

# Create app if it doesn't exist
APP_NAME="sf-state-scraper-$(date +%s)"
heroku create $APP_NAME

# Add Chrome buildpacks for Selenium
heroku buildpacks:add --index 1 heroku/python
heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-google-chrome.git
heroku buildpacks:add --index 3 https://github.com/heroku/heroku-buildpack-chromedriver.git

# Deploy to Heroku
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Open the app
heroku open

echo "✅ Deployed to: https://$APP_NAME.herokuapp.com" 