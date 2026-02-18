# 🐳 Docker Deployment Guide

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- Docker Compose v2.0+

### Initial Setup

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file with your values:**
   - Set a strong `POSTGRES_PASSWORD`
   - Set a secure `SECRET_KEY` (min 32 characters)
   - Update `ALLOWED_ORIGINS` with your domain

3. **Build and start all services:**
   ```bash
   docker-compose up -d --build
   ```

4. **Check service health:**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

5. **Run database migrations:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

6. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## Service Architecture

### Database (PostGIS PostgreSQL)
- **Image:** `postgis/postgis:14-3.3`
- **Port:** 5432
- **Volume:** `postgres_data` (persistent storage)
- **Health Check:** Automatic pg_isready monitoring

### Backend (FastAPI)
- **Base:** `python:3.11-slim`
- **Port:** 8000
- **Features:**
  - PostGIS support
  - Automatic restart
  - Volume mount for data persistence

### Frontend (React + Nginx)
- **Multi-stage build:** Node 18 (build) → Nginx Alpine (serve)
- **Port:** 80
- **Features:**
  - Gzip compression
  - SPA routing support
  - API proxying to backend
  - Security headers (X-Frame-Options, XSS Protection)
  - Static asset caching (1 year)

---

## Common Commands

### Start services
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f [service_name]
```

### Rebuild a service
```bash
docker-compose up -d --build backend
```

### Access a container shell
```bash
docker-compose exec backend /bin/bash
docker-compose exec database psql -U property_user -d property_db
```

### Run backend tests
```bash
docker-compose exec backend pytest tests/ -v
```

---

## Production Deployment

### Security Checklist
- [ ] Change all default passwords
- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure HTTPS/SSL certificates
- [ ] Update `ALLOWED_ORIGINS` to your domain only
- [ ] Enable firewall rules (ports 80, 443, 22 only)

### Recommended Enhancements
1. **Use Docker Secrets** for sensitive data
2. **Add Traefik/Caddy** for automatic HTTPS
3. **Configure backup cron** for PostgreSQL
4. **Set up monitoring** (Prometheus + Grafana)
5. **Implement log aggregation** (ELK stack)

---

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs [service_name]

# Check resource usage
docker stats
```

### Database connection issues
```bash
# Verify database is healthy
docker-compose ps

# Check network connectivity
docker-compose exec backend ping database
```

### Frontend can't reach backend
- Verify `REACT_APP_API_BASE_URL` in `.env`
- Check nginx proxy configuration
- Ensure backend is running: `docker-compose ps backend`

### Rebuild from scratch
```bash
docker-compose down -v  # WARNING: Deletes volumes!
docker-compose up -d --build
```

---

## Data Persistence

All data is stored in Docker volumes:
- `postgres_data`: Database files
- Backend `./data`: Mounted from host (allows data ingestion scripts)

**Backup database:**
```bash
docker-compose exec database pg_dump -U property_user property_db > backup.sql
```

**Restore database:**
```bash
cat backup.sql | docker-compose exec -T database psql -U property_user property_db
```
