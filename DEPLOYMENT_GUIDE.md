# VidyaSetu Deployment Guide - Render.com + Netlify

## Overview
This guide deploys the full-stack VidyaSetu application:
- **Backend**: FastAPI on Render.com (Free Tier)
- **Database**: PostgreSQL on Render.com (Free Tier)
- **Frontend**: React/Vite on Netlify (Free Tier)

## Prerequisites

1. **GitHub Account** - for code hosting
2. **Render.com Account** - for backend deployment
3. **Netlify Account** - for frontend deployment
4. **Git** - for version control

---

## **Phase 1: Prepare GitHub Repository**

### 1.1 Push Code to GitHub

```powershell
cd c:\Users\Abhis\Document\Abhishek_code\SE\OpsCraft
git init
git add .
git commit -m "Initial commit for deployment"
git remote add origin https://github.com/YOUR_USERNAME/OpsCraft.git
git branch -M main
git push -u origin main
```

### 1.2 Update `backend/.env.example` (if not exists)

Ensure this file exists for production:

```env
DATABASE_URL=postgresql://user:password@host/vidyasetu
SECRET_KEY=change-me-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
APP_NAME=VidyaSetu
DEBUG=false
BASE_URL=https://vidyasetu-backend.onrender.com
FRONTEND_ORIGINS=https://vidyasetu-frontend.netlify.app

# AI Settings
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL_NAME=gemini-flash-latest
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com
GEMINI_TIMEOUT_SECONDS=60
AI_RATE_LIMIT_BACKEND=database
```

---

## **Phase 2: Deploy Backend on Render.com**

### 2.1 Create Render.com Account
1. Go to https://render.com
2. Sign up with GitHub (easy integration)
3. Click "New +" → "Web Service"

### 2.2 Connect GitHub Repository
1. Click "Connect a repository"
2. Authorize GitHub
3. Select your **OpsCraft** repository

### 2.3 Configure Render Service
1. **Name**: `vidyasetu-backend`
2. **Runtime**: Docker
3. **Branch**: `main`
4. **Region**: `Oregon` (free tier)
5. **Plan**: Free

### 2.4 Set Environment Variables (in Render Dashboard)

Add these in **Environment** section:

```
DATABASE_URL = (auto-filled from PostgreSQL)
SECRET_KEY = (generate a random string or keep default)
DEBUG = false
BASE_URL = https://vidyasetu-backend.onrender.com
FRONTEND_ORIGINS = https://vidyasetu-frontend.netlify.app,https://vidyasetu-backend.onrender.com
GEMINI_API_KEY = (your Gemini API key)
AI_RATE_LIMIT_BACKEND = database
```

### 2.5 Create PostgreSQL Database on Render
1. In Render Dashboard, click "New +" → "PostgreSQL"
2. **Name**: `vidyasetu-db`
3. **Region**: `Oregon`
4. **Database Name**: `vidyasetu`
5. **Plan**: Free
6. Click "Create Database"

### 2.6 Deploy
1. Set `Root Directory`: `backend`
2. Set `Build Command`: (auto-detected from Dockerfile)
3. Set `Start Command`: (auto-detected from Dockerfile)
4. Click "Deploy"
5. **Wait 5-10 minutes** for build & deployment

### 2.7 Database Initialization (CRITICAL! ⚠️)

**The Dockerfile now automatically:**
- Runs database migrations (schema creation)
- Seeds default users and institution on first deployment

✅ **Default login credentials (created automatically):**
- **Email**: `admin@vidyasetu.edu`
- **Password**: `admin123`
- **Role**: Admin

Other seeded users:
- Institution Admin: `institution.admin@vidyasetu.edu` / `institution123`
- Educator: `educator@vidyasetu.edu` / `educator123`
- Student: `student@vidyasetu.edu` / `student123`

**If seeding fails or you need to reseed manually:**
```bash
# SSH into Render container and run:
python -m scripts.init_db
```

✅ Backend will be running at: `https://vidyasetu-backend.onrender.com`

---

## **Phase 3: Deploy Frontend on Netlify**

### 3.1 Create Netlify Account
1. Go to https://netlify.com
2. Click "Sign up"
3. Choose "GitHub" as login method

### 3.2 Create New Site
1. Click "Add new site" → "Import an existing project"
2. Select GitHub, then select your **OpsCraft** repository

### 3.3 Configure Build Settings
1. **Team**: Select your team
2. **Repository**: OpsCraft
3. **Branch**: `main`
4. **Build Command**: `cd frontend && npm run build`
5. **Publish Directory**: `frontend/dist`

### 3.4 Set Environment Variables (in Netlify)
1. Go to **Site settings** → **Build & deploy** → **Environment**
2. Add Variable:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: `https://vidyasetu-backend.onrender.com`

### 3.5 Deploy
1. Click "Deploy site"
2. **Wait 2-3 minutes** for build & deployment

✅ Frontend will be running at: `https://vidyasetu-frontend.netlify.app` (or your custom domain)

---

## **Phase 4: Post-Deployment Checks**

### 4.1 Verify Backend
```
GET https://vidyasetu-backend.onrender.com/docs
```
Should open Swagger API documentation.

### 4.2 Verify Database
```
GET https://vidyasetu-backend.onrender.com/api/v1/users/me
```
Should return 401 Unauthorized (expected without login).

### 4.3 Verify Frontend
```
Visit https://vidyasetu-frontend.netlify.app
```
Should load the login page.

### 4.4 Test Login
Use default credentials:
- Email: `admin@vidyasetu.edu`
- Password: `admin123`

---

## **Phase 5: Custom Domain (Optional)**

### For Backend (Render)
1. Go to Render Dashboard
2. Your service → **Settings** → **Custom Domain**
3. Add your domain (e.g., `api.yourdomain.com`)

### For Frontend (Netlify)
1. Go to Netlify Site Settings
2. **Domain management** → **Add custom domain**
3. Add your domain (e.g., `www.yourdomain.com`)

---

## **Troubleshooting**

### Backend won't start
- Check Render logs: Dashboard → Service → **Logs**
- Common issues:
  - Missing GEMINI_API_KEY
  - Database connection error
  - Port not set correctly

### Frontend not connecting to backend
- Check browser console: F12 → **Console**
- Verify `VITE_API_BASE_URL` in Netlify environment variables
- Check CORS settings in backend `.env` (FRONTEND_ORIGINS)

### Database migration failed
- SSH into Render service: Dashboard → **Shell**
- Run: `python -m alembic upgrade head`

### File uploads not working
- Ensure `/media` directory is writable
- Consider using S3/Cloud Storage for production

---

## **Monitoring & Logs**

### Render Backend Logs
1. Go to Render Dashboard
2. Your service → **Logs**
3. Real-time logs visible here

### Netlify Frontend Logs
1. Go to Netlify Site Dashboard
2. **Deploys** → Click latest deploy
3. View build logs

---

## **Cost Analysis (Free Tier)**

| Service | Free Tier | Cost |
|---------|-----------|------|
| Render Web Service | 0.5 CPU, 512MB RAM | Free (sleeps after 15 min inactivity) |
| Render PostgreSQL | 256MB storage, 1 backup | Free |
| Netlify Hosting | Unlimited bandwidth | Free |
| **Total Monthly** | | **$0** |

**Note**: Free tier services auto-spin down after 15 minutes of inactivity. Upgrade to Pro if needed.

---

## **Next Steps**

1. Push code to GitHub
2. Create Render account and connect repository
3. Create PostgreSQL database
4. Set environment variables
5. Deploy backend
6. Create Netlify account
7. Connect frontend repository
8. Deploy frontend
9. Test the live application

---

## **Support**

- Render Docs: https://render.com/docs
- Netlify Docs: https://docs.netlify.com
- FastAPI Docs: https://fastapi.tiangolo.com
- React/Vite Docs: https://vitejs.dev
