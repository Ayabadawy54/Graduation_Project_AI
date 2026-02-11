# 🐳 Quick Docker Start

## Option 1: With Docker Compose (Recommended)

```bash
# Copy environment file
cp .env.example .env

# Start all services (PostgreSQL + API + Jupyter + Nginx + Redis)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

**Access:**
- API Swagger: http://localhost:8000/docs
- Jupyter: http://localhost:8888
- Nginx: http://localhost

## Option 2: API Only (Quick Test)

```bash
# Build
docker build -t talentree-api .

# Run
docker run -p 8000:8000 talentree-api
```

**Access:** http://localhost:8000/docs

## Option 3: With PostgreSQL

```bash
# Start database first
docker-compose up -d postgres

# Wait 10 seconds for DB to be ready
sleep 10

# Start API
docker-compose up -d api
```

## Stop Services

```bash
docker-compose down
```

## Full Documentation

See `docs/DOCKER_DEPLOYMENT.md` for complete guide.
