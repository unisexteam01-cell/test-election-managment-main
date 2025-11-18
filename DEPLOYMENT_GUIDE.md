# Deployment Guide - MongoDB Atlas & Full Stack

## Quick Start

### 1. Configure MongoDB Atlas

```bash
cd backend
python setup_mongo_atlas.py
```

This will prompt you for:
- MongoDB username
- MongoDB password
- Cluster URL
- Database name (optional)

### 2. Test MongoDB Connection

```bash
python test_mongo_connection.py
```

Expected output:
```
✅ Connection successful!
✅ Database 'test-election' selected
✅ All tests passed! MongoDB Atlas is configured correctly.
```

### 3. Start Backend with MongoDB Atlas

```bash
cd backend
uvicorn server:app --reload --port 8004
```

You should see:
```
✅ Successfully connected to MongoDB Atlas!
✅ Using database: test-election
✅ Connected to MongoDB and indexes created
```

### 4. Configure Frontend Backend URL

#### Option A: Development (Local Emulator)
```bash
export EXPO_PUBLIC_BACKEND_URL='http://10.0.2.2:8004'
cd frontend
npm start
```

#### Option B: Development (Physical Device/LAN)
```bash
export EXPO_PUBLIC_BACKEND_URL='http://192.168.1.YOUR_IP:8004'
cd frontend
npm start
```

#### Option C: Production (EAS Build)
Already configured in `frontend/eas.json`

### 5. Build & Deploy with EAS

```bash
cd frontend
eas build --platform android --profile preview
```

The app will be available in your Expo dashboard.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌──────────────────┐          ┌──────────────────┐            │
│  │   React Native   │          │    Web Browser   │            │
│  │   Mobile App     │          │                  │            │
│  └────────┬─────────┘          └────────┬─────────┘            │
│           │                             │                       │
│           └─────────────┬───────────────┘                       │
│                         │                                       │
│                    HTTP/HTTPS                                  │
│                         │                                       │
│           ┌─────────────▼─────────────┐                        │
│           │   FastAPI Backend         │                        │
│           │   (uvicorn)               │                        │
│           │   Port: 8004              │                        │
│           └─────────────┬─────────────┘                        │
│                         │                                       │
│                    TCP Connection                              │
│                         │                                       │
│           ┌─────────────▼─────────────┐                        │
│           │  MongoDB Atlas            │                        │
│           │  Cloud Database           │                        │
│           │  (mongodb+srv://)         │                        │
│           └─────────────────────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Environment Configuration

### Backend (.env)
```ini
# MongoDB Atlas
MONGO_URL=mongodb+srv://user:password@cluster0.mongodb.net/?retryWrites=true&w=majority
DB_NAME=test-election

# Server
PORT=8004
ENVIRONMENT=development
```

### Frontend (.env.local or export)
```bash
EXPO_PUBLIC_BACKEND_URL=http://10.0.2.2:8004  # Development
EXPO_PUBLIC_BACKEND_URL=http://192.168.1.143:8004  # LAN
EXPO_PUBLIC_BACKEND_URL=https://api.yourdomain.com  # Production
```

---

## Database Management

### Collections Created Automatically

The backend creates these collections on startup:

```
├── users          - User accounts & authentication
├── voters         - Voter data (main collection)
├── families       - Family groupings
├── surveys        - Survey responses
├── survey_templates - Survey templates
├── tasks          - Task assignments
├── issues         - Reported issues
└── influencers    - Community influencers
```

### Accessing MongoDB Atlas Console

1. Go to https://www.mongodb.com/cloud/atlas
2. Click your cluster
3. Click "Collections" to browse data
4. Click "Performance" to monitor queries
5. Click "Charts" for analytics

---

## Deployment Scenarios

### Development (Local Machine)
```bash
# Terminal 1: Backend
cd backend
python test_mongo_connection.py  # Verify connection
uvicorn server:app --reload --port 8004

# Terminal 2: Frontend
cd frontend
export EXPO_PUBLIC_BACKEND_URL='http://10.0.2.2:8004'
npm start
```

### Staging (Cloud Backend)
```bash
# Backend on Heroku/Railway/Render:
MONGO_URL="mongodb+srv://..." uvicorn server:app --port 8000

# Frontend:
export EXPO_PUBLIC_BACKEND_URL='https://staging-api.herokuapp.com'
eas build --platform android --profile staging
```

### Production (Full Cloud)

#### Step 1: Deploy Backend
```bash
# Option A: Heroku
heroku login
cd backend
heroku create election-app-backend
heroku config:set MONGO_URL="mongodb+srv://..."
heroku config:set DB_NAME="test-election-prod"
git push heroku main

# Option B: Railway
railway login
cd backend
railway init
railway up
```

#### Step 2: Build Frontend for Production
```bash
cd frontend
EXPO_PUBLIC_BACKEND_URL='https://election-app-backend.herokuapp.com' \
eas build --platform android --profile production
```

---

## Troubleshooting

### MongoDB Connection Issues

**Error: "Server selection timeout"**
- Check MongoDB Atlas cluster is running
- Verify IP whitelist includes your IP
- Test with: `python test_mongo_connection.py`

**Error: "Authentication failed"**
- Verify username/password in MONGO_URL
- Check special characters are URL-encoded
- Reset password in MongoDB Atlas if needed

### Frontend Connection Issues

**Error: "Network Error" on login**
- Verify backend is running: `curl http://10.0.2.2:8004/api/health`
- Check EXPO_PUBLIC_BACKEND_URL matches backend address
- For physical device, ensure on same WiFi network

**Error: "Failed to resolve backend host"**
- On emulator: Use `http://10.0.2.2:8004`
- On physical device: Use LAN IP like `http://192.168.1.143:8004`
- Check firewall isn't blocking port 8004

### Database Issues

**Error: "Collection already exists"**
- MongoDB Atlas handles this automatically
- Safe to restart app multiple times

**Error: "Indexes not created"**
- Check backend logs during startup
- Verify database user has write permissions
- Check MONGO_URL includes correct database name

---

## Monitoring & Maintenance

### Monitor Backend
```bash
# Check if running
lsof -i :8004

# View recent logs
tail -f backend.log
```

### Monitor Database
1. MongoDB Atlas Console → Metrics
2. Check: Connection count, operations/sec
3. Review slow queries in "Performance Advisor"

### Backup Data
```bash
# Manual backup
mongoexport --uri="$MONGO_URL" \
  --collection=voters \
  --out=voters_backup.json

# Restore
mongoimport --uri="$MONGO_URL" \
  --collection=voters \
  --file=voters_backup.json
```

---

## Security Checklist

- [ ] Change default MongoDB password
- [ ] Restrict MongoDB IP whitelist
- [ ] Use strong passwords (16+ chars, mixed case)
- [ ] Enable HTTPS for frontend (production)
- [ ] Set up SSL certificates
- [ ] Enable database encryption (Atlas M10+)
- [ ] Configure backup retention
- [ ] Review and limit database user permissions
- [ ] Set up monitoring and alerts
- [ ] Document recovery procedures
- [ ] Regular security audits

---

## Support & Resources

- **MongoDB Atlas Docs**: https://docs.atlas.mongodb.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Expo Docs**: https://docs.expo.dev
- **Project README**: See main README.md
- **MongoDB Atlas Setup**: See MONGODB_ATLAS_SETUP.md
