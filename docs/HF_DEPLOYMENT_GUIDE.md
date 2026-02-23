# 🚀 Deploy to Hugging Face Spaces — Step by Step

## What You Need
- GitHub account ✅ (you have it)
- Hugging Face account (free, no card)

---

## Step 1: Create Hugging Face Account
1. Go to [huggingface.co](https://huggingface.co)
2. Click **Sign Up** → use email (no card needed)
3. Verify email

---

## Step 2: Create a New Space

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in:
   - **Space name:** `talentree-admin-api`
   - **License:** MIT
   - **SDK:** Select **Docker** ← important!
   - **Visibility:** Public
3. Click **Create Space**

---

## Step 3: Replace the Dockerfile

Hugging Face Spaces requires port **7860**.  
Your repo has `Dockerfile.spaces` already prepared for this.

In your Space repo, the `Dockerfile` must use port 7860.

**Option A — Use the HF Space Git directly:**
```bash
# Clone the HF Space repo
git clone https://huggingface.co/spaces/YOUR_USERNAME/talentree-admin-api
cd talentree-admin-api

# Copy all your project files into it
# (or link it to GitHub — see Option B below)
```

**Option B (Recommended) — Link GitHub to HF Space:**
1. In your Space settings → **Repository** tab
2. Click **"Link to GitHub repository"**
3. Select: `Ayabadawy54/Graduation_Project_AI`
4. Branch: `feature/admin-dashboard`
5. ✅ Auto-deploys on every push!

---

## Step 4: Set the Right Dockerfile

Since HF uses port 7860, rename `Dockerfile.spaces` → `Dockerfile` in the Space:

If using GitHub link, add this to your repo's root:

```bash
# In your local project:
copy Dockerfile.spaces Dockerfile.hf
# Then in HF Space settings, set Dockerfile path to Dockerfile.spaces
```

**OR (Easiest):** In HF Space Settings → Dockerfile path → type `Dockerfile.spaces`

---

## Step 5: Wait for Build

HF will:
1. Pull your code from GitHub
2. Build the Docker image (~3-5 minutes first time)
3. Start the container on port 7860

You'll see **build logs** live in the Space page.

---

## Step 6: Your Live API URL

Once deployed:
```
https://YOUR_USERNAME-talentree-admin-api.hf.space

Swagger UI:
https://YOUR_USERNAME-talentree-admin-api.hf.space/docs

Example endpoint:
https://YOUR_USERNAME-talentree-admin-api.hf.space/api/admin/dashboard/overview
```

---

## Step 7: Backend Team Integration

Backend team replaces `localhost:8000` with your HF URL:

```javascript
// Before (local only):
const API_BASE = "http://localhost:8000/api/admin"

// After (deployed, always available):
const API_BASE = "https://YOUR_USERNAME-talentree-admin-api.hf.space/api/admin"
```

---

## ⚠️ Important Notes

| Item | Detail |
|---|---|
| **Port** | HF requires 7860 (done in `Dockerfile.spaces`) |
| **Sleep** | HF Free spaces sleep after 48h inactivity — first request wakes it (~30s) |
| **Storage** | CSV files are inside the image — no external DB needed |
| **Auto-deploy** | Every `git push` triggers rebuild automatically |
| **CORS** | Already configured in `main.py` for all origins |

---

## 🔄 Updating the API Later

```bash
# Make your changes locally
git add .
git commit -m "fix: ..."
git push origin feature/admin-dashboard
# → HF Space auto-rebuilds in ~3 minutes ✅
```

---

## 📞 Need Help?

Check build logs inside your HF Space page — all errors show there.  
Common issue: `requirements.txt` missing a package → add it and push again.
