# Deployment Guide

Comprehensive guide for deploying AI Engine to production environments.

## Deployment Options

### Docker (Recommended)

**Build Image**:
```bash
docker build -t ai-engine:latest .
docker tag ai-engine:latest pyramidxc/ai-engine:latest
docker push pyramidxc/ai-engine:latest
```

**Run Container**:
```bash
docker run -d \
  --name ai-engine \
  -p 8000:8000 \
  -e OPENAI_API_KEY=sk-your-key \
  -e OPENAI_MODEL=gpt-4o-mini \
  -v /var/log/ai-engine:/app/logs \
  pyramidxc/ai-engine:latest
```

**Docker Compose**:
```bash
docker-compose up -d
```

### Kubernetes

**Deployment Manifest**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-engine
  template:
    metadata:
      labels:
        app: ai-engine
    spec:
      containers:
      - name: ai-engine
        image: pyramidxc/ai-engine:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-engine-secrets
              key: openai-key
        livenessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ai-engine
spec:
  selector:
    app: ai-engine
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Virtual Machine

**System Requirements**:
- Ubuntu 20.04+ or similar
- Python 3.10+
- 2GB RAM minimum, 4GB recommended
- 20GB disk space

**Installation**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.10 python3-pip -y

# Clone and setup
git clone https://github.com/pyramidxc/ai-engine.git
cd ai-engine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure systemd service
sudo tee /etc/systemd/system/ai-engine.service > /dev/null <<EOF
[Unit]
Description=AI Engine Service
After=network.target

[Service]
Type=simple
User=ai-engine
WorkingDirectory=/opt/ai-engine
Environment="PATH=/opt/ai-engine/venv/bin"
EnvironmentFile=/etc/ai-engine/.env
ExecStart=/opt/ai-engine/venv/bin/python -m app.main
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl enable ai-engine
sudo systemctl start ai-engine
```

## Configuration for Production

### Environment Variables

```bash
# Application
DEBUG=false
LOG_LEVEL=INFO

# OpenAI
OPENAI_API_KEY=sk-your-production-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=60

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Security
ALLOWED_HOSTS=api.example.com
CORS_ORIGINS=https://app.example.com
```

### SSL/TLS

Use reverse proxy (Nginx/Apache) for TLS termination:

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    ssl_certificate /etc/ssl/certs/api.example.com.crt;
    ssl_certificate_key /etc/ssl/private/api.example.com.key;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Rate Limiting

Configure in reverse proxy:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /analyze {
    limit_req zone=api_limit burst=20;
    proxy_pass http://localhost:8000;
}
```

## Monitoring & Logging

### Application Logs

```bash
# View logs
tail -f logs/token_usage.jsonl

# Archive old logs
find logs -name "*.jsonl" -mtime +30 -exec gzip {} \;

# Parse token usage
cat logs/token_usage.jsonl | jq '.total_tokens' | awk '{sum+=$1} END {print sum}'
```

### Health Checks

```bash
# Liveness check
curl http://localhost:8000/ready

# Status check
curl http://localhost:8000/status
```

### Metrics to Monitor

- Request latency (target: <20s)
- Error rate (target: <0.1%)
- Token usage trends
- API key quota usage
- Response validation rate

## Scaling

### Horizontal Scaling

```bash
# Multiple instances behind load balancer
docker run -d --name ai-engine-1 -p 8001:8000 ai-engine
docker run -d --name ai-engine-2 -p 8002:8000 ai-engine
docker run -d --name ai-engine-3 -p 8003:8000 ai-engine

# Use Nginx for load balancing
upstream ai_engine {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    location / {
        proxy_pass http://ai_engine;
    }
}
```

### Performance Tuning

- Enable connection pooling
- Implement response caching (Redis)
- Use async workers
- Monitor database connections
- Optimize LLM prompts

## Backup & Disaster Recovery

### Log Backups

```bash
# Daily backup
0 2 * * * tar -czf /backup/logs-$(date +\%Y\%m\%d).tar.gz /var/log/ai-engine
```

### Configuration Backups

```bash
# Backup .env and configs
tar -czf config-backup-$(date +%Y%m%d).tar.gz .env docker-compose.yml
```

## Incident Response

### Service Down

1. Check container/process status
2. Review logs for errors
3. Verify OpenAI API status
4. Check network connectivity
5. Restart service if needed

### High Error Rate

1. Check OpenAI API status
2. Review recent changes
3. Analyze error logs
4. Check rate limits
5. Rollback if necessary

### Performance Degradation

1. Check system resources (CPU, memory)
2. Monitor OpenAI API latency
3. Review request patterns
4. Check for stuck requests
5. Consider scaling

## Security Hardening

### Container Security

```dockerfile
# Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Minimal base image
FROM python:3.11-slim

# No privileged operations
RUN pip install --user -r requirements.txt
```

### Network Security

- Use private networks where possible
- Implement WAF rules
- Enable DDoS protection
- Use TLS everywhere
- Implement rate limiting

### API Security

- Rotate API keys regularly
- Monitor key usage
- Implement API authentication
- Log all requests
- Use VPN for internal access

## Related Documentation

- [Architecture](ARCHITECTURE.md) - System design
- [Operations Runbook](RUNBOOK.md) - Day-to-day operations
- [Security](../SECURITY.md) - Security guidelines
- [Support](../SUPPORT.md) - Troubleshooting

---

Last updated: 2024
