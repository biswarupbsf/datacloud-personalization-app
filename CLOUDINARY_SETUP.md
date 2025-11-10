# 🎨 Cloudinary Setup for Face-Swap Image Generation

## Why Cloudinary?
Cloudinary provides **free cloud storage** for images, giving Fal.ai's face-swap models public URLs to access your profile pictures. This enables true hyper-personalized content generation.

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Create Free Cloudinary Account
1. Go to: https://cloudinary.com/users/register_free
2. Sign up (100% free tier - no credit card needed)
3. Verify your email

### Step 2: Get Your Credentials
After logging in to Cloudinary dashboard:

1. Click **"Dashboard"** in the top menu
2. You'll see your credentials:
   - **Cloud Name**: (e.g., `dzxxx`)
   - **API Key**: (e.g., `123456789012345`)
   - **API Secret**: (e.g., `abcdefghijklmnop-qrstuvwxyz`)

### Step 3: Add to Heroku

Run these commands in your terminal:

```bash
heroku config:set CLOUDINARY_CLOUD_NAME="your_cloud_name"
heroku config:set CLOUDINARY_API_KEY="your_api_key"
heroku config:set CLOUDINARY_API_SECRET="your_api_secret"
```

**Example:**
```bash
heroku config:set CLOUDINARY_CLOUD_NAME="dzxxx"
heroku config:set CLOUDINARY_API_KEY="123456789012345"
heroku config:set CLOUDINARY_API_SECRET="abcdefghijklmnop-qrstuvwxyz"
```

### Step 4: Restart Heroku
```bash
heroku restart
```

---

## ✅ Verify Setup

After restart, go to your app and generate a personalized image. Check the Heroku logs:

```bash
heroku logs --tail
```

You should see:
- ✅ `"Uploading base64 image to Cloudinary..."`
- ✅ `"Uploaded successfully: https://res.cloudinary.com/..."`
- ✅ Face-swap generation starting

---

## 🎯 Features Unlocked

With Cloudinary + Fal.ai, your app will:

✨ **True Face-Swap**: Uses actual profile pictures in generated images  
✨ **Hyper-Personalized**: Each person's face in custom scenarios  
✨ **Professional Quality**: High-res campaign images  
✨ **Scalable**: Generate for all 100 profiles  
✨ **Auto-Optimization**: Face detection and cropping

---

## 🔄 Fallback Behavior

**Without Cloudinary**: App uses Fal.ai's built-in upload (may have limitations)  
**Without FAL_KEY**: App shows demo placeholder images  
**With Both**: Full hyper-personalized face-swap generation! 🚀

---

## 📊 Free Tier Limits

Cloudinary Free Plan:
- ✅ 25 GB storage
- ✅ 25 GB bandwidth/month
- ✅ Unlimited transformations
- ✅ Perfect for this use case!

---

## 🆘 Troubleshooting

**Issue**: "Cloudinary not configured"  
**Fix**: Make sure all 3 environment variables are set on Heroku

**Issue**: "Upload failed"  
**Fix**: Check API Secret is correct (it's case-sensitive)

**Issue**: "Face-swap still not working"  
**Fix**: Check Heroku logs for specific error messages

---

## 🎨 Ready to Generate!

Once configured, your workflow is:
1. Upload profile pictures → Stored as base64 in JSON
2. Click "Generate Image" → Uploads to Cloudinary → Face-swap with Fal.ai
3. Get hyper-personalized campaign content! 🎉

