# 🚀 VidyaSetu Deployment Checklist

## Pre-Deployment ✓

- [ ] Update `.gitignore` to exclude `.env` files
- [ ] Ensure `requirements.txt` is up to date
- [ ] Test locally: Backend and frontend running
- [ ] Commit all changes: `git commit -m "Ready for deployment"`

## GitHub Setup ✓

- [ ] Create GitHub account (if needed)
- [ ] Create new repository: `OpsCraft`
- [ ] Push code: `git push -u origin main`
- [ ] Verify files are on GitHub

## Backend Deployment (Render.com) ✓

### Account & Repository
- [ ] Create Render.com account (sign up with GitHub)
- [ ] New Web Service → Connect GitHub → Select OpsCraft

### Configuration
- [ ] Set Root Directory: `backend`
- [ ] Runtime: Docker (auto-detected)
- [ ] Region: Oregon (free tier)
- [ ] Plan: Free

### Database
- [ ] Create PostgreSQL database on Render
- [ ] Database name: `vidyasetu`
- [ ] Region: Oregon
- [ ] Plan: Free
- [ ] Copy connection string to clipboard

### Environment Variables
- [ ] `DATABASE_URL` = (from PostgreSQL)
- [ ] `SECRET_KEY` = (random string or keep default)
- [ ] `DEBUG` = `false`
- [ ] `BASE_URL` = `https://vidyasetu-backend.onrender.com`
- [ ] `FRONTEND_ORIGINS` = `https://vidyasetu-frontend.netlify.app`
- [ ] `GEMINI_API_KEY` = (your Gemini API key)
- [ ] `AI_RATE_LIMIT_BACKEND` = `database`

### Deploy
- [ ] Click "Deploy"
- [ ] Wait 5-10 minutes for build
- [ ] Check Logs for errors
- [ ] Verify: https://vidyasetu-backend.onrender.com/docs

## Frontend Deployment (Netlify) ✓

### Account & Repository
- [ ] Create Netlify account (sign up with GitHub)
- [ ] Add new site → Import existing project
- [ ] Select OpsCraft repository

### Build Settings
- [ ] Build command: `cd frontend && npm run build`
- [ ] Publish directory: `frontend/dist`
- [ ] Branch: `main`

### Environment Variables
- [ ] `VITE_API_BASE_URL` = `https://vidyasetu-backend.onrender.com`

### Deploy
- [ ] Save and trigger deploy
- [ ] Wait 2-3 minutes for build
- [ ] Check deploy logs
- [ ] Verify: https://vidyasetu-frontend.netlify.app

## Post-Deployment Testing ✓

### Backend API
- [ ] [ ] Visit https://vidyasetu-backend.onrender.com/docs (should load Swagger UI)
- [ ] [ ] GET /api/v1/users/me (should return 401 without auth)

### Frontend
- [ ] [ ] Visit https://vidyasetu-frontend.netlify.app (should load login page)
- [ ] [ ] Login with admin@vidyasetu.edu / admin123
- [ ] [ ] Check browser console (F12) for errors
- [ ] [ ] Test a few features (e.g., view dashboard)

### Database
- [ ] [ ] Verify data persists (log out, log back in)
- [ ] [ ] Check Render PostgreSQL dashboard for disk usage

## Optional Enhancements ✓

- [ ] Add custom domain for backend (Render)
- [ ] Add custom domain for frontend (Netlify)
- [ ] Enable Netlify CDN for better performance
- [ ] Set up automated backups for PostgreSQL
- [ ] Add monitoring/alerts on Render
- [ ] Enable SSL certificate (auto with Render)

## Troubleshooting Checklist ✓

If deployment fails:
- [ ] Check Render backend logs: Service → Logs
- [ ] Check Netlify frontend logs: Deploys → [latest] → Deploy logs
- [ ] Verify GitHub push was successful
- [ ] Verify environment variables are set correctly
- [ ] Check CORS origin in backend `.env`
- [ ] Verify Docker build (Render shows build steps)

---

## Support Links

- **Render**: https://render.com/docs
- **Netlify**: https://docs.netlify.com
- **FastAPI**: https://fastapi.tiangolo.com
- **Vite**: https://vitejs.dev

---

## Timeline

- **GitHub Setup**: ~2 minutes
- **Backend Deployment**: ~10 minutes
- **Frontend Deployment**: ~5 minutes
- **Total**: ~20 minutes

**Start time:** __________ | **End time:** __________
