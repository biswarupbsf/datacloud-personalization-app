#!/bin/bash

# 🚀 Data Cloud App - Heroku Deployment Script
# This script automates the deployment process to Heroku

set -e  # Exit on error

echo "========================================================================"
echo "🚀 DATA CLOUD APP - HEROKU DEPLOYMENT"
echo "========================================================================"
echo ""

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed!"
    echo "📥 Install from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo "✅ Heroku CLI detected"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📂 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
    echo ""
fi

# Add all files
echo "📝 Adding files to Git..."
git add .
echo "✅ Files added"
echo ""

# Commit changes
echo "💾 Committing changes..."
read -p "Enter commit message (or press Enter for default): " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="Deploy Data Cloud App to Heroku"
fi
git commit -m "$commit_msg" || echo "⚠️  No changes to commit (this is OK)"
echo ""

# Check if Heroku remote exists
if git remote | grep -q heroku; then
    echo "✅ Heroku remote already configured"
    HEROKU_APP=$(heroku apps:info -r heroku | grep "Web URL" | awk '{print $3}')
    echo "📍 App URL: $HEROKU_APP"
else
    echo "🆕 Creating new Heroku app..."
    read -p "Enter app name (leave blank for auto-generated): " app_name
    
    if [ -z "$app_name" ]; then
        heroku create
    else
        heroku create "$app_name"
    fi
    
    echo "✅ Heroku app created"
fi

echo ""
echo "🔐 Setting environment variables..."

# Prompt for Salesforce credentials (optional)
read -p "Do you want to set Salesforce credentials now? (y/n): " set_creds

if [ "$set_creds" == "y" ] || [ "$set_creds" == "Y" ]; then
    read -p "Salesforce Username: " sf_username
    read -sp "Salesforce Password: " sf_password
    echo ""
    read -sp "Salesforce Security Token: " sf_token
    echo ""
    
    heroku config:set SF_USERNAME="$sf_username"
    heroku config:set SF_PASSWORD="$sf_password"
    heroku config:set SF_SECURITY_TOKEN="$sf_token"
    
    echo "✅ Salesforce credentials set"
else
    echo "⏭️  Skipping Salesforce credentials (you can set them later)"
fi

echo ""
echo "🚀 Deploying to Heroku..."
git push heroku main || git push heroku master

echo ""
echo "⚙️  Scaling web dyno..."
heroku ps:scale web=1

echo ""
echo "========================================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "========================================================================"
echo ""

# Get app URL
APP_URL=$(heroku apps:info | grep "Web URL" | awk '{print $3}')
echo "🌐 Your app is live at: $APP_URL"
echo ""

# Open app in browser
read -p "Open app in browser? (y/n): " open_app
if [ "$open_app" == "y" ] || [ "$open_app" == "Y" ]; then
    heroku open
fi

echo ""
echo "📊 View logs with: heroku logs --tail"
echo "🔄 Update app with: git push heroku main"
echo "⚙️  Manage app at: https://dashboard.heroku.com/"
echo ""
echo "========================================================================"
echo "🎉 Happy deploying!"
echo "========================================================================"


