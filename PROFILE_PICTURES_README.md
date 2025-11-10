# Profile Pictures - Important Information

## ⚠️ Known Issue: Profile Pictures Reset on Deploy

**Problem:** When you upload custom profile pictures via the web interface, they are stored as base64 data in `data/synthetic_engagement.json`. However, **every time the code is redeployed to Heroku, this file gets overwritten** with the version from git, causing you to **lose all uploaded pictures**.

## 🔧 Current Workaround

After each code deployment, you need to re-upload your profile pictures:

1. Go to: https://infinite-lowlands-00393-eacde66da597.herokuapp.com/upload-profile-picture
2. Upload pictures for each person again

## 💡 Permanent Solutions (Future Implementation)

### Option 1: Use Heroku Postgres (Recommended)
- Store profile pictures in a PostgreSQL database
- Database persists across deployments
- **Cost:** Free tier available

### Option 2: Use Cloudinary Permanent Storage
- Upload pictures directly to Cloudinary
- Store only the Cloudinary URL in JSON
- **Cost:** Free tier available

### Option 3: Use Amazon S3
- Upload to S3 bucket
- Store S3 URLs in JSON
- **Cost:** Pay per usage

### Option 4: Manual Backup/Restore Script
- Download data before deploy
- Restore after deploy
- **Cost:** Free but manual process

## 📝 For Now: How to Preserve Your Uploads

**Before deploying new code:**

```bash
# 1. Download current data from Heroku
heroku run "cat data/synthetic_engagement.json" --app infinite-lowlands-00393 > backup_engagement.json

# 2. Deploy your code
git push heroku main

# 3. Restore your data (via web interface or API)
# Use the Upload Profile Picture page to re-upload
```

## 🎯 Best Practice

Until a permanent solution is implemented:
- **Use DiceBear avatars for development/testing**
- **Upload real photos only for production demos**
- **Keep a local copy of profile pictures** for quick re-upload

## 📸 Current Status

- **Biswarup Banerjee:** DiceBear avatar (upload real photo if needed)
- **Ashish Desai:** DiceBear avatar
- **Deepika Chauhan:** DiceBear avatar
- **Rajesh Rao:** DiceBear avatar
- **Archana Tripathi:** DiceBear avatar

All DiceBear avatars work perfectly with the AI image generation system!

