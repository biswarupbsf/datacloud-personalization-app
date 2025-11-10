# 🎨 Replicate API Setup for True Face-Swap

## ✅ What You Get

Replicate provides **TRUE face-swap** capabilities using industry-standard models:
- ✅ **Your actual face** in generated images
- ✅ **Free tier** with credits to start
- ✅ **Production-ready** quality
- ✅ **Simple integration**

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Create Replicate Account

1. Go to: https://replicate.com
2. Click **"Sign Up"**
3. Use your GitHub or Google account
4. ✅ **Free tier includes credits!**

### Step 2: Get Your API Token

1. After signing in, go to: https://replicate.com/account/api-tokens
2. Click **"Create Token"**
3. Copy your token (looks like: `r8_xxx...`)

### Step 3: Add to Heroku

Run this command in your terminal:

```bash
heroku config:set REPLICATE_API_TOKEN="your_token_here"
```

**Example:**
```bash
heroku config:set REPLICATE_API_TOKEN="r8_abc123xyz456..."
```

### Step 4: Setup Cloudinary (Required!)

Replicate needs public URLs for profile pictures. Use Cloudinary (free):

1. Sign up: https://cloudinary.com/users/register_free
2. Get credentials from dashboard
3. Set on Heroku:

```bash
heroku config:set CLOUDINARY_CLOUD_NAME="your_cloud_name"
heroku config:set CLOUDINARY_API_KEY="your_api_key"
heroku config:set CLOUDINARY_API_SECRET="your_api_secret"
```

### Step 5: Restart Heroku

```bash
heroku restart
```

---

## 🎯 How It Works

### Two-Step Face-Swap Process:

**Step 1: Generate Base Scene**
- Uses Stability AI's SDXL model
- Creates realistic scene based on your prompt
- Example: "Person running on treadmill in premium gym"

**Step 2: Face-Swap**
- Uses Replicate's `yan-ops/face_swap` model
- Swaps the face from base scene with your profile picture
- Maintains lighting, pose, and context

### Result:
**Your face** running on treadmill in Nike gear with Singapore skyline! 🎉

---

## 💰 Pricing (Very Affordable)

Replicate charges per generation:
- **SDXL**: ~$0.0055 per image
- **Face-swap**: ~$0.0023 per image
- **Total per image**: ~$0.008 (less than 1 cent!)

**Free tier gives you:**
- Credits to start
- ~100-200 test generations

---

## 🎨 Generate Your First Image

1. **Upload Profile Picture**
   - Go to: https://infinite-lowlands-00393-eacde66da597.herokuapp.com/upload-profile-picture
   - Select "Biswarup Banerjee"
   - Upload your photo
   - Click "Upload Picture"

2. **Generate Image**
   - Go to: https://infinite-lowlands-00393-eacde66da597.herokuapp.com/personalized-images
   - Select "Biswarup Banerjee"
   - Use suggested prompt or custom one
   - Click "Generate Personalized Image"
   - Wait ~45-60 seconds (two-step process)

3. **See Results**
   - Base scene (generic person)
   - Final image (YOUR face swapped in!)
   - Download button

---

## ✨ What Makes This Hyper-Personalized

For **Biswarup Banerjee**, the AI creates:

🏃 **Scene**: Running on treadmill (from "Running" hobby)  
👟 **Gear**: Nike athletic wear (from "Nike" brand)  
🌏 **Background**: Singapore skyline (from "Singapore" destination)  
💪 **Setting**: Premium gym (from "Active" lifestyle)  
👤 **Face**: **YOUR ACTUAL FACE** (from profile picture!)

Every profile gets unique images based on their complete data!

---

## 🔧 Troubleshooting

**Error: "REPLICATE_API_TOKEN not set"**
→ Run: `heroku config:set REPLICATE_API_TOKEN="your_token"`

**Error: "Could not prepare face image"**
→ Set up Cloudinary (required for public URLs)

**Error: "Prediction failed"**
→ Check Replicate dashboard for usage limits

**Generation takes too long**
→ Normal! Two-step process takes 45-60 seconds

**Face doesn't look right**
→ Use a clear, front-facing profile picture with good lighting

---

## 📊 Check Usage & Costs

Monitor your usage at:
- https://replicate.com/account/billing

You can set spending limits to avoid surprises!

---

## 🎉 Ready to Generate!

Once both tokens are set (Replicate + Cloudinary), you're ready to create **true hyper-personalized campaign images** with face-swap! 🚀

**Next steps:**
1. Set REPLICATE_API_TOKEN
2. Set Cloudinary credentials
3. Restart Heroku
4. Upload profile picture
5. Generate your first face-swapped image!

