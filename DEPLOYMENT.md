# Deployment Guide

This guide covers various deployment options for dev-companion.

## Table of Contents
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Production Considerations](#production-considerations)

---

## Local Development

### Quick Setup

```bash
# Clone repository
git clone https://github.com/self-reliantkid/dev-companion.git
cd dev-companion

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run application
streamlit run app.py
```

### Development Mode

```bash
# Install development dependencies
pip install pytest pytest-cov flake8 black isort mypy

# Run tests
pytest tests/ -v

# Run with auto-reload
streamlit run app.py --server.runOnSave true
```

---

## Docker Deployment

### Using Docker

**Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Build and run:**
```bash
# Build image
docker build -t dev-companion:latest .

# Run container
docker run -p 8501:8501 \
  -e WATSONX_API_KEY=your_key \
  -e WATSONX_PROJECT_ID=your_project \
  -e WATSONX_URL=https://us-south.ml.cloud.ibm.com \
  dev-companion:latest
```

### Using Docker Compose

**Create docker-compose.yml:**
```yaml
version: '3.8'

services:
  dev-companion:
    build: .
    ports:
      - "8501:8501"
    environment:
      - WATSONX_API_KEY=${WATSONX_API_KEY}
      - WATSONX_PROJECT_ID=${WATSONX_PROJECT_ID}
      - WATSONX_URL=${WATSONX_URL}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    volumes:
      - ./metrics.json:/app/metrics.json
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Run with Docker Compose:**
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Cloud Deployment

### Streamlit Cloud

1. **Push to GitHub:**
   ```bash
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select `app.py` as the main file
   - Add secrets in the dashboard:
     ```toml
     WATSONX_API_KEY = "your_key"
     WATSONX_PROJECT_ID = "your_project"
     WATSONX_URL = "https://us-south.ml.cloud.ibm.com"
     ```

3. **Deploy!** Your app will be live at `https://your-app.streamlit.app`

### Heroku

**Create Procfile:**
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**Deploy:**
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set WATSONX_API_KEY=your_key
heroku config:set WATSONX_PROJECT_ID=your_project
heroku config:set WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Deploy
git push heroku main

# Open app
heroku open
```

### AWS EC2

**Launch EC2 instance:**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx -y

# Clone repository
git clone https://github.com/self-reliantkid/dev-companion.git
cd dev-companion

# Setup application
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
nano .env  # Add your credentials

# Run with systemd
sudo nano /etc/systemd/system/dev-companion.service
```

**Systemd service file:**
```ini
[Unit]
Description=dev-companion Streamlit App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/dev-companion
Environment="PATH=/home/ubuntu/dev-companion/venv/bin"
ExecStart=/home/ubuntu/dev-companion/venv/bin/streamlit run app.py --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable dev-companion
sudo systemctl start dev-companion
```

### Google Cloud Run

**Create cloudbuild.yaml:**
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/dev-companion', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/dev-companion']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'dev-companion'
      - '--image=gcr.io/$PROJECT_ID/dev-companion'
      - '--platform=managed'
      - '--region=us-central1'
      - '--allow-unauthenticated'
```

**Deploy:**
```bash
gcloud builds submit --config cloudbuild.yaml
```

---

## Production Considerations

### Security

1. **Environment Variables:**
   - Never commit `.env` files
   - Use secret management services (AWS Secrets Manager, etc.)
   - Rotate API keys regularly

2. **HTTPS:**
   - Always use HTTPS in production
   - Use Let's Encrypt for free SSL certificates
   - Configure proper CORS headers

3. **Rate Limiting:**
   - Implement rate limiting to prevent abuse
   - Monitor API usage and costs
   - Set up alerts for unusual activity

### Performance

1. **Caching:**
   - Enable response caching
   - Use Redis for distributed caching
   - Cache IAM tokens (already implemented)

2. **Scaling:**
   - Use load balancers for multiple instances
   - Implement horizontal scaling
   - Monitor resource usage

3. **Monitoring:**
   - Set up application monitoring (New Relic, Datadog)
   - Track metrics and quality scores
   - Configure error alerting

### Backup & Recovery

1. **Data Backup:**
   ```bash
   # Backup metrics
   cp metrics.json metrics.backup.json
   
   # Backup configuration
   tar -czf config-backup.tar.gz .env bob_sessions/ docs/
   ```

2. **Disaster Recovery:**
   - Document recovery procedures
   - Test backup restoration regularly
   - Keep multiple backup copies

### Maintenance

1. **Updates:**
   ```bash
   # Update dependencies
   pip install --upgrade -r requirements.txt
   
   # Run tests
   pytest tests/ -v
   
   # Restart service
   sudo systemctl restart dev-companion
   ```

2. **Monitoring:**
   - Check logs regularly
   - Monitor API costs
   - Review quality metrics
   - Update documentation

### Cost Optimization

1. **API Usage:**
   - Enable caching to reduce API calls
   - Set token limits appropriately
   - Monitor daily/monthly costs

2. **Infrastructure:**
   - Use auto-scaling to match demand
   - Shut down dev instances when not in use
   - Use spot instances for non-critical workloads

---

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `WATSONX_API_KEY` | Yes | IBM watsonx.ai API key | `your_api_key` |
| `WATSONX_PROJECT_ID` | Yes | IBM watsonx.ai project ID | `your_project_id` |
| `WATSONX_URL` | Yes | IBM watsonx.ai endpoint URL | `https://us-south.ml.cloud.ibm.com` |
| `GITHUB_TOKEN` | No | GitHub personal access token | `ghp_xxxxx` |
| `LOG_LEVEL` | No | Logging level | `INFO` |
| `MAX_RETRIES` | No | Maximum retry attempts | `2` |
| `MIN_QUALITY_THRESHOLD` | No | Minimum quality score | `0.7` |
| `ENABLE_METRICS` | No | Enable metrics collection | `true` |
| `ENABLE_VALIDATION` | No | Enable response validation | `true` |

---

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find process using port 8501
lsof -i :8501
# Kill process
kill -9 <PID>
```

**Module not found:**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

**API authentication failed:**
- Verify API key is correct
- Check project ID matches your watsonx.ai project
- Ensure URL is correct for your region

**Out of memory:**
- Reduce max_tokens parameter
- Enable streaming mode
- Increase instance memory

---

## Support

For deployment issues:
- Check [GitHub Issues](https://github.com/self-reliantkid/dev-companion/issues)
- Review [SECURITY.md](SECURITY.md) for security concerns
- See [CONTRIBUTING.md](CONTRIBUTING.md) for development help

---

**Last Updated:** 2026-05-18  
**Version:** 2.1.0