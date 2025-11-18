# MongoDB Atlas Setup Guide

## Overview
This project uses MongoDB Atlas for cloud database management. MongoDB Atlas is a fully managed MongoDB cloud database service.

## Prerequisites
1. MongoDB Atlas Account (https://www.mongodb.com/cloud/atlas)
2. Cluster created in MongoDB Atlas
3. Database user with appropriate permissions

## Setup Instructions

### 1. Create MongoDB Atlas Cluster
- Go to MongoDB Atlas (https://www.mongodb.com/cloud/atlas)
- Sign in or create an account
- Create a new cluster (free tier available)
- Wait for cluster to be ready (~5-10 minutes)

### 2. Get Connection String
- Click "Connect" on your cluster
- Choose "Connect your application"
- Select "Python" as the driver
- Copy the connection string

### 3. Create Database User
- In MongoDB Atlas, go to "Database Access"
- Create a new user with appropriate password
- Grant roles: "readWriteAnyDatabase"

### 4. Configure Environment Variables
Add the following to `backend/.env`:

```
MONGO_URL=mongodb+srv://<username>:<password>@<cluster-url>/?retryWrites=true&w=majority&appName=Cluster0
DB_NAME=test-election
```

Replace:
- `<username>`: Your MongoDB Atlas user
- `<password>`: Your MongoDB Atlas password (URL-encoded if contains special characters)
- `<cluster-url>`: Your cluster URL (e.g., cluster0.wwo605i.mongodb.net)

### 5. IP Whitelist
- In MongoDB Atlas, go to "Network Access"
- Add IP addresses that will connect to the cluster
- Or allow access from anywhere: `0.0.0.0/0` (for development only)

### 6. Test Connection
```bash
cd backend
python -m pytest tests/test_connection.py
```

## Database Collections

The application automatically creates the following collections:

### Core Collections
- **users**: User accounts and authentication
- **voters**: Voter information and profiles
- **families**: Family groupings
- **booths**: Voting booths

### Campaign Data
- **surveys**: Survey responses
- **survey_templates**: Survey question templates
- **tasks**: Assigned tasks
- **issues**: Reported issues
- **influencers**: Community influencers

## Indexes
All collections have optimized indexes created automatically on startup. Key indexes include:

### Users
- `username` (unique)
- `email` (unique)
- `role` (lookup)

### Voters
- `voter_id` (unique)
- Full-text search on name/address
- `booth_number` + `voted_status` (compound)
- `assigned_to` + `visited_status` (compound)
- `area` + `favor_score` (compound)

## Data Backup & Recovery

### Automatic Backups
MongoDB Atlas provides:
- Automated daily backups
- 7-day retention for free tier
- Point-in-time recovery (paid tier)

### Manual Backup
```bash
# Export collection
mongoexport --uri="mongodb+srv://user:pass@cluster0.mongodb.net/test-election" \
  --collection=voters \
  --out=voters_backup.json

# Import collection
mongoimport --uri="mongodb+srv://user:pass@cluster0.mongodb.net/test-election" \
  --collection=voters \
  --file=voters_backup.json
```

## Production Checklist

- [ ] Use strong passwords for database users
- [ ] Restrict IP whitelist to known addresses
- [ ] Enable authentication on all users
- [ ] Set up monitoring and alerts
- [ ] Configure automatic backups
- [ ] Test backup/restore procedure
- [ ] Document recovery procedures
- [ ] Set up connection pooling
- [ ] Monitor query performance
- [ ] Enable encryption at rest (Atlas M10+)

## Troubleshooting

### Connection Issues
1. Check IP whitelist in MongoDB Atlas
2. Verify credentials in .env file
3. Ensure MONGO_URL has correct format
4. Check network connectivity

### Performance Issues
1. Review indexes in MongoDB Atlas console
2. Check Atlas metrics and monitoring
3. Analyze slow queries
4. Consider upgrading tier

### Authentication Issues
1. Verify user exists in Database Access
2. Check password is correctly URL-encoded
3. Ensure user has correct roles
4. Reset password if needed

## Environment-Specific Configuration

### Development
```
MONGO_URL=mongodb+srv://dev_user:password@cluster0.wwo605i.mongodb.net/?retryWrites=true&w=majority
DB_NAME=test-election-dev
```

### Staging
```
MONGO_URL=mongodb+srv://staging_user:password@cluster0.wwo605i.mongodb.net/?retryWrites=true&w=majority
DB_NAME=test-election-staging
```

### Production
```
MONGO_URL=mongodb+srv://prod_user:password@cluster0.wwo605i.mongodb.net/?retryWrites=true&w=majority
DB_NAME=test-election-prod
```

## Support
For MongoDB Atlas support: https://www.mongodb.com/support
For application issues: See main README.md
