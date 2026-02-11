# 🐳 Docker Deployment Guide - TalentTree Admin Dashboard

**Version:** 4.0.0  
**Last Updated:** February 12, 2026

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Services Overview](#services-overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### **One Command Deployment:**

```bash
# Clone repository
git clone -b feature/admin-dashboard https://github.com/Ayabadawy54/Graduation_Project_AI.git
cd Graduation_Project_AI

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

**That's it!** 🎉

---

## 📦 Services Overview

Your Docker Compose setup includes **5 services**:

| Service | Port | Purpose | URL |
|---------|------|---------|-----|
| **PostgreSQL** | 5432 | Production database | - |
| **FastAPI API** | 8000 | REST API backend | http://localhost:8000/docs |
| **Jupyter** | 8888 | Notebooks server | http://localhost:8888 |
| **Nginx** | 80 | Reverse proxy | http://localhost |
| **Redis** | 6379 | Cache (optional) | - |

---

## 🔧 Prerequisites

### **Required:**

✅ **Docker** (20.10+)
```bash
docker --version
```

✅ **Docker Compose** (2.0+)
```bash
docker-compose --version
```

### **Installation:**

**Windows:**
- Download Docker Desktop: https://www.docker.com/products/docker-desktop

**Mac:**
```bash
brew install docker docker-compose
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
```

---

## 📥 Installation

### **Step 1: Clone Repository**

```bash
git clone -b feature/admin-dashboard https://github.com/Ayabadawy54/Graduation_Project_AI.git
cd Graduation_Project_AI
```

### **Step 2: Configure Environment**

```bash
# Copy example environment file
cp .env.example .env

# Edit if needed (optional)
nano .env  # or any text editor
```

### **Step 3: Build Images**

```bash
# Build all services
docker-compose build

# Or build with no cache
docker-compose build --no-cache
```

---

## 🎯 Usage

### **Start Services**

```bash
# Start all services in background
docker-compose up -d

# Start and view logs
docker-compose up

# Start specific service
docker-compose up -d api
```

### **Stop Services**

```bash
# Stop all services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove volumes (CAUTION: deletes data!)
docker-compose down -v
```

### **View Logs**

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres
```

### **Check Status**

```bash
# List running containers
docker-compose ps

# Check health
docker-compose ps

# Resource usage
docker stats
```

---

## 🌐 Access Points

Once services are running:

### **1. FastAPI Swagger UI** 📚
```
http://localhost:8000/docs
```
- Interactive API documentation
- Test all 52 endpoints
- View request/response schemas

### **2. ReDoc API Documentation** 📖
```
http://localhost:8000/redoc
```
- Alternative API docs
- Better for reading

### **3. Jupyter Notebooks** 📊
```
http://localhost:8888
```
- Access all 11 notebooks
- Run analytics
- View visualizations

### **4. Nginx Proxy** 🔀
```
http://localhost/api/dashboard/overview
http://localhost/docs
http://localhost/jupyter/
```
- Unified entry point
- Load balancing ready

### **5. PostgreSQL Database** 🗄️
```
Host: localhost
Port: 5432
Database: talentree
User: talentree_user
Password: talentree_password_2026
```

---

## ⚙️ Configuration

### **Environment Variables**

Edit `.env` file:

```bash
# Database
DATABASE_URL=postgresql://talentree_user:password@postgres:5432/talentree
POSTGRES_PASSWORD=your_secure_password

# API
ENVIRONMENT=development  # or production
SECRET_KEY=your_secret_key_here

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://yourdomain.com
```

### **Docker Compose Profiles**

```bash
# Development (all services)
docker-compose --profile dev up -d

# Production (API + DB only)
docker-compose --profile prod up -d

# Minimal (API only with mock data)
docker-compose up -d api
```

---

## 🛠️ Common Commands

### **Database Operations**

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U talentree_user -d talentree

# Run SQL script
docker-compose exec postgres psql -U talentree_user -d talentree < init-db.sql

# Backup database
docker-compose exec postgres pg_dump -U talentree_user talentree > backup.sql

# Restore database
docker-compose exec -T postgres psql -U talentree_user talentree < backup.sql
```

### **Load Mock Data**

```bash
# Copy CSV files to PostgreSQL container
docker cp mock_data/users.csv talentree-db:/tmp/

# Import CSV
docker-compose exec postgres psql -U talentree_user -d talentree -c "\COPY users FROM '/tmp/users.csv' DELIMITER ',' CSV HEADER"

# Or use Python script inside API container
docker-compose exec api python scripts/load_data_to_db.py
```

### **Container Management**

```bash
# Restart service
docker-compose restart api

# Rebuild single service
docker-compose up -d --build api

# Execute command in container
docker-compose exec api python -c "print('Hello')"

# Shell access
docker-compose exec api bash
docker-compose exec postgres bash
```

---

## 🐛 Troubleshooting

### **Issue: Containers won't start**

```bash
# Check logs
docker-compose logs

# Check docker daemon
docker ps

# Restart docker service
sudo systemctl restart docker  # Linux
# or restart Docker Desktop
```

### **Issue: Port already in use**

```bash
# Find process using port
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Mac/Linux

# Kill process or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use port 8001 instead
```

### **Issue: Database connection failed**

```bash
# Wait for PostgreSQL to be ready
docker-compose up -d postgres
sleep 10
docker-compose up -d api

# Or check health
docker-compose exec postgres pg_isready
```

### **Issue: Out of disk space**

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything (CAUTION!)
docker system prune -a --volumes
```

### **Issue: Permission denied**

```bash
# Linux/Mac: Fix permissions
sudo chown -R $USER:$USER .

# Or run with sudo
sudo docker-compose up -d
```

---

## 📊 Monitoring

### **Health Checks**

```bash
# API health
curl http://localhost:8000/docs

# Database health
docker-compose exec postgres pg_isready -U talentree_user

# Nginx health
curl http://localhost/health
```

### **Resource Monitoring**

```bash
# Real-time stats
docker stats

# Disk usage
docker system df

# Container resource limits
docker-compose exec api cat /sys/fs/cgroup/memory/memory.limit_in_bytes
```

---

## 🔒 Security Notes

### **For Development:**

✅ Default passwords are fine  
✅ No SSL required  
✅ Debug mode enabled  

### **For Production:**

⚠️ Change all default passwords  
⚠️ Use environment variables  
⚠️ Enable SSL/TLS  
⚠️ Restrict CORS origins  
⚠️ Disable debug mode  
⚠️ Use secret management (AWS Secrets Manager, etc.)  

---

## 🚀 Production Deployment

### **Production Docker Compose:**

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    build: .
    restart: always
    environment:
      ENVIRONMENT: production
      DATABASE_URL: ${DATABASE_URL}  # From secrets
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

### **Deploy to Production:**

```bash
# Build for production
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Scale API
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

---

## 📝 Best Practices

### **Development:**

✅ Use `docker-compose up` to see logs  
✅ Mount volumes for hot reload  
✅ Use `.env` file for secrets  
✅ Commit `docker-compose.yml` to git  
✅ Don't commit `.env` to git  

### **Production:**

✅ Use specific image tags (not `latest`)  
✅ Enable health checks  
✅ Set resource limits  
✅ Use external volumes for data  
✅ Implement backup strategy  
✅ Monitor logs and metrics  

---

## 🎯 Next Steps

### **1. Verify Deployment:**
```bash
# Check all services
docker-compose ps

# Test API
curl http://localhost:8000/api/dashboard/overview

# Open Jupyter
open http://localhost:8888
```

### **2. Load Data:**
```bash
# Import CSV to database (optional)
docker-compose exec api python scripts/load_data_to_db.py
```

### **3. Explore:**
- Open Swagger UI: http://localhost:8000/docs
- Run notebooks: http://localhost:8888
- Test endpoints

### **4. Integrate Frontend:**
- Point frontend to http://localhost:8000
- Use API documentation
- Test all features

---

## 📚 Additional Resources

- **Docker Documentation:** https://docs.docker.com
- **Docker Compose Reference:** https://docs.docker.com/compose/
- **PostgreSQL Docker:** https://hub.docker.com/_/postgres
- **FastAPI Docker:** https://fastapi.tiangolo.com/deployment/docker/

---

## 🆘 Support

**Issues?**
1. Check logs: `docker-compose logs -f`
2. Review troubleshooting section above
3. File issue on GitHub
4. Contact: ai@talentree.eg

---

**🐳 Happy Dockerizing!**

**Status:** ✅ Ready for Deployment  
**Version:** 4.0.0  
**Last Updated:** February 12, 2026
