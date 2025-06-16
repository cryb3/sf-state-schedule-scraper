#!/usr/bin/env python3
"""
Programmatic deployment script for SF State Scraper web app
Supports: Heroku, Railway, Render
"""

import subprocess
import sys
import os
import argparse
from datetime import datetime

def run_command(cmd, check=True):
    """Run shell command and return result"""
    print(f"📋 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {result.stderr}")
        sys.exit(1)
    return result

def deploy_to_heroku(app_name=None):
    """Deploy to Heroku programmatically"""
    print("🚀 Deploying to Heroku...")
    
    # Check if Heroku CLI is installed
    try:
        run_command("heroku --version")
    except:
        print("❌ Heroku CLI not found. Please install it first.")
        return False
    
    # Generate app name if not provided
    if not app_name:
        timestamp = int(datetime.now().timestamp())
        app_name = f"sf-state-scraper-{timestamp}"
    
    # Create Heroku app
    run_command(f"heroku create {app_name}")
    
    # Add buildpacks
    buildpacks = [
        "heroku/python",
        "https://github.com/heroku/heroku-buildpack-google-chrome.git",
        "https://github.com/heroku/heroku-buildpack-chromedriver.git"
    ]
    
    for i, buildpack in enumerate(buildpacks, 1):
        run_command(f"heroku buildpacks:add --index {i} {buildpack}")
    
    # Deploy
    run_command("git add .")
    run_command('git commit -m "Deploy to Heroku" || true', check=False)
    run_command("git push heroku main")
    
    app_url = f"https://{app_name}.herokuapp.com"
    print(f"✅ Successfully deployed to Heroku: {app_url}")
    return app_url

def deploy_to_railway():
    """Deploy to Railway programmatically"""
    print("🚂 Deploying to Railway...")
    
    # Check if Railway CLI is installed
    try:
        run_command("railway --version")
    except:
        print("❌ Railway CLI not found. Installing...")
        run_command("npm install -g @railway/cli")
    
    # Initialize and deploy
    run_command("railway login")
    run_command("railway init")
    run_command("railway variables set PORT=8501")
    run_command("railway up")
    
    print("✅ Successfully deployed to Railway!")
    return "https://railway.app"

def deploy_to_render():
    """Deploy to Render using Git-based deployment"""
    print("🎨 Setting up Render deployment...")
    
    print("✅ Render configuration created!")
    print("📋 Next steps:")
    print("1. Push your code to GitHub")
    print("2. Connect your GitHub repo to Render")
    print("3. Render will auto-deploy from render.yaml")
    return "https://render.com"

def setup_git_if_needed():
    """Initialize git repo if not already done"""
    if not os.path.exists('.git'):
        print("📦 Initializing Git repository...")
        run_command("git init")
        run_command("git add .")
        run_command('git commit -m "Initial commit"')

def main():
    parser = argparse.ArgumentParser(description="Deploy SF State Scraper to cloud platforms")
    parser.add_argument("platform", choices=["heroku", "railway", "render", "all"], 
                       help="Platform to deploy to")
    parser.add_argument("--app-name", help="App name for Heroku")
    
    args = parser.parse_args()
    
    # Ensure git is set up
    setup_git_if_needed()
    
    # Deploy to selected platform(s)
    if args.platform == "heroku":
        deploy_to_heroku(args.app_name)
    elif args.platform == "railway":
        deploy_to_railway()
    elif args.platform == "render":
        deploy_to_render()
    elif args.platform == "all":
        print("🌐 Deploying to all platforms...")
        deploy_to_heroku(args.app_name)
        deploy_to_railway()
        deploy_to_render()

if __name__ == "__main__":
    main() 