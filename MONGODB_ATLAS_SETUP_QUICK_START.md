# MongoDB Atlas Configuration - Next Steps

## ✅ Completed Setup

I've configured your application to use MongoDB Atlas. Here's what was set up:

### Created Files:
1. **`backend/.env`** - MongoDB Atlas configuration template
2. **`backend/test_mongo_connection.py`** - Connection test script
3. **`backend/setup_mongo_atlas.py`** - Interactive setup script
4. **`backend/MONGODB_ATLAS_SETUP.md`** - Detailed setup guide
5. **`DEPLOYMENT_GUIDE.md`** - Full deployment instructions

### Updated Files:
1. **`backend/database.py`** - Enhanced MongoDB connection with error handling
2. **`frontend/package.json`** - Fixed expo-font peer dependency

---

## 🔧 Configure Your MongoDB Atlas Credentials

Your MongoDB Atlas connection string was provided:
```
mongodb+srv://sahil:<db_password>@cluster0.wwo605i.mongodb.net/?appName=Cluster0
```

### Step 1: Update `.env` with Your Password

Edit `backend/.env` and replace `<db_password>` with your actual MongoDB password:

```bash
# Before (placeholder)
MONGO_URL=mongodb+srv://sahil:<db_password>@cluster0.wwo605i.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

# After (with your password)
MONGO_URL=mongodb+srv://sahil:your_actual_password@cluster0.wwo605i.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

**Important:** If your password contains special characters (like `@`, `#`, `:`), you must URL-encode them:
- `@` → `%40`
- `#` → `%23`
- `:` → `%3A`

Example:
```
Password: p@ss#word:123
URL-encoded: p%40ss%23word%3A123
MONGO_URL: mongodb+srv://sahil:p%40ss%23word%3A123@cluster0.wwo605i.mongodb.net/...
```

### Step 2: Configure IP Whitelist in MongoDB Atlas

1. Go to https://www.mongodb.com/cloud/atlas
2. Click your cluster → **Network Access**
3. Click **"Add IP Address"**
4. Add your IP address OR allow `0.0.0.0/0` for development
5. Click **"Confirm"**

### Step 3: Test the Connection

```bash
cd backend
source venv/bin/activate
python test_mongo_connection.py
```

Expected output:
```
✅ Connection successful!
✅ Database 'test-election' selected
✅ All tests passed! MongoDB Atlas is configured correctly.
```

---

## 🚀 Start the Application

### Backend with MongoDB Atlas

```bash
cd backend
source venv/bin/activate
uvicorn server:app --reload --port 8004
```

You should see:
```
✅ Successfully connected to MongoDB Atlas!
✅ Using database: test-election
✅ Connected to MongoDB and indexes created
INFO:     Uvicorn running on http://127.0.0.1:8004
```

### Frontend (in another terminal)

```bash
cd frontend
export EXPO_PUBLIC_BACKEND_URL='http://10.0.2.2:8004'
npm start
```

---

## 📱 Test the Full Stack

### In Android Emulator:

1. Start backend (see above)
2. Start frontend Metro bundler (see above)
3. In emulator, press `a` to open Android app
4. Test login with your credentials
5. Verify data is saved in MongoDB Atlas

### Verify Data in MongoDB Atlas:

1. Go to MongoDB Atlas → Cluster → **Collections**
2. You should see:
   - `users` collection (with your login user)
   - `voters` collection (if any imported)
   - Other collections as data is added

---

## 🔄 Deployment to Production

### Deploy Backend to Cloud (Heroku/Railway/Render)

Example for Heroku:
```bash
# Install Heroku CLI
brew install heroku

# Login
heroku login

# Create app
heroku create election-app-backend

# Set environment variables
heroku config:set -a election-app-backend MONGO_URL="mongodb+srv://sahil:your_password@cluster0.wwo605i.mongodb.net/?retryWrites=true&w=majority"
heroku config:set -a election-app-backend DB_NAME="test-election"

# Deploy
git push heroku main
```

### Build Production Android App

```bash
cd frontend
EXPO_PUBLIC_BACKEND_URL='https://election-app-backend.herokuapp.com' \
eas build --platform android --profile production
```

---

## 📋 Quick Reference

### Database Connection Test
```bash
cd backend && source venv/bin/activate && python test_mongo_connection.py
```

### View MongoDB Data
1. MongoDB Atlas console: https://www.mongodb.com/cloud/atlas
2. Click cluster → Collections
3. Browse any collection

### Backend Health Check
```bash
curl http://localhost:8004/api/health
```

### Frontend Backend Configuration
- **Development (Emulator):** `http://10.0.2.2:8004`
- **Development (Physical Device):** `http://192.168.1.YOUR_IP:8004`
- **Production:** Set in `EXPO_PUBLIC_BACKEND_URL` environment variable

---

## ✨ Features Enabled

With MongoDB Atlas setup:

✅ Cloud database (no local MongoDB needed)
✅ Automatic backups
✅ Scalable infrastructure
✅ Network security features
✅ Monitoring & alerts
✅ Data encryption
✅ Global availability

---

## 🆘 Troubleshooting

### Connection Error: "Authentication failed"
- [ ] Verify password in `.env` is correct
- [ ] Check password doesn't need URL encoding
- [ ] Verify username is "sahil"
- [ ] Check database user exists in MongoDB Atlas

### Connection Error: "Server selection timeout"
- [ ] Check cluster is active in MongoDB Atlas
- [ ] Verify IP is whitelisted (add 0.0.0.0/0 for dev)
- [ ] Check internet connection
- [ ] Verify cluster URL: `cluster0.wwo605i.mongodb.net`

### Frontend Login Error: "Network Error"
- [ ] Verify backend is running: `curl http://10.0.2.2:8004/api/health`
- [ ] Check `EXPO_PUBLIC_BACKEND_URL` matches backend address
- [ ] For physical device: ensure on same WiFi, use LAN IP
- [ ] Check firewall isn't blocking port 8004

### No Data in MongoDB Atlas
- [ ] Check correct database name: "test-election"
- [ ] Verify user has write permissions
- [ ] Check app didn't error during startup
- [ ] Review backend logs for errors

---

## 📚 More Resources

- **MongoDB Atlas Docs**: https://docs.atlas.mongodb.com
- **Full Setup Guide**: See `backend/MONGODB_ATLAS_SETUP.md`
- **Deployment Options**: See `DEPLOYMENT_GUIDE.md`
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Expo Docs**: https://docs.expo.dev

---

## ✅ Checklist

- [ ] Updated `backend/.env` with your MongoDB password
- [ ] Added IP to MongoDB Atlas whitelist
- [ ] Tested connection with `python test_mongo_connection.py`
- [ ] Started backend: `uvicorn server:app --reload`
- [ ] Started frontend: `npm start`
- [ ] Tested login in emulator/device
- [ ] Verified data appears in MongoDB Atlas console

Once all items are checked, your application is ready for development and can be deployed to production!
