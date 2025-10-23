# Operational Runbook

Day-to-day operational procedures for AI Engine.

## Service Management

### Check Service Status

```bash
# Docker
docker ps -a | grep ai-engine
docker logs ai-engine

# Kubernetes
kubectl get deployments -l app=ai-engine
kubectl logs -l app=ai-engine

# Systemd
systemctl status ai-engine
journalctl -u ai-engine -f
```

### Start/Stop Service

```bash
# Docker
docker start ai-engine
docker stop ai-engine

# Kubernetes
kubectl scale deployment ai-engine --replicas=3

# Systemd
sudo systemctl start ai-engine
sudo systemctl stop ai-engine
```

### View Logs

```bash
# Recent 100 lines
tail -100 logs/token_usage.jsonl

# Stream logs
tail -f logs/token_usage.jsonl

# Parse logs (jq required)
cat logs/token_usage.jsonl | jq '.model_used, .total_tokens'

# Count errors
grep -c "error\|failed" logs/token_usage.jsonl
```

## Common Tasks

### Test Endpoint

```bash
# Health check
curl http://localhost:8000/ready

# Status
curl http://localhost:8000/status

# Full analysis (uses example request)
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d @examples/requests/linux_web_server_enhanced.json
```

### Monitor Performance

```bash
# Watch request metrics
watch 'tail -50 logs/token_usage.jsonl | jq -s "length"'

# Check recent token usage
jq -s 'add | {requests: length, total_tokens: .total_tokens | add, avg_tokens: (.total_tokens | add / length)}' \
  logs/token_usage.jsonl
```

### Check API Quota

Monitor OpenAI API usage:
- Portal: https://platform.openai.com/account/usage
- Typically check daily for usage spikes

## Troubleshooting

### Service Won't Start

1. Check logs: `docker logs ai-engine`
2. Verify API key: `echo $OPENAI_API_KEY`
3. Test connectivity: `curl https://api.openai.com`
4. Restart service: `docker restart ai-engine`

### High Error Rate

1. Check logs for pattern: `grep -i error logs/token_usage.jsonl`
2. Verify API key is valid
3. Check OpenAI status page
4. Review recent code changes
5. Consider rollback if needed

### Performance Degradation

1. Monitor system resources: `top`, `free`, `df`
2. Check network connectivity
3. Monitor OpenAI API latency
4. Review current load
5. Consider scaling if needed

### Memory Leak

1. Monitor memory: `watch free -h`
2. Check for stuck processes: `ps aux | grep python`
3. Review recent code changes
4. Restart service if necessary
5. Investigate core dump

## Regular Maintenance

### Daily

- Monitor error logs
- Check API quota usage
- Review request metrics
- Verify service is responding

### Weekly

- Archive old logs
- Review performance trends
- Check disk space usage
- Test disaster recovery procedures

### Monthly

- Full system review
- Security updates
- Dependency updates
- Performance optimization analysis

## Backup Procedures

### Manual Backup

```bash
# Backup configuration
tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz .env *.yml *.yaml

# Archive logs
gzip logs/*.jsonl
mv logs/*.jsonl.gz archives/

# Store offsite
scp backup-*.tar.gz backup@offsite-server:/backups/
```

### Automated Backup (Cron)

```bash
# Add to crontab
0 2 * * * tar -czf /backup/ai-engine-$(date +\%Y\%m\%d).tar.gz /opt/ai-engine/.env /opt/ai-engine/docker-compose.yml

# Verify cron job
crontab -l
```

## Disaster Recovery

### Service Failure Recovery

1. Identify failure cause from logs
2. Determine if restart is needed
3. If code issue, rollback to last working version
4. Verify service recovers
5. Monitor for 30 minutes

### Data Loss Recovery

1. Stop service immediately
2. Restore from backup
3. Verify restore integrity
4. Resume service
5. Monitor for consistency issues

### API Key Compromise

1. Revoke compromised key immediately
2. Generate new key
3. Update environment
4. Restart service
5. Monitor for unusual activity

## Performance Tuning

### Optimize Response Times

- Reduce prompt complexity (if needed)
- Use faster model (gpt-4o-mini is default)
- Implement caching for similar requests
- Monitor token usage trends

### Resource Optimization

- Monitor CPU usage (target: <80%)
- Monitor memory usage (target: <75%)
- Monitor disk usage (target: <80%)
- Add resources if needed

## Security Maintenance

### Rotate Credentials

```bash
# Generate new API key in OpenAI dashboard
# Update .env
nano .env

# Restart service to load new key
docker restart ai-engine

# Verify new key works
curl http://localhost:8000/ready
```

### Security Updates

```bash
# Check for updates
pip list --outdated

# Update dependencies
pip install --upgrade -r requirements.txt

# Test thoroughly
pytest

# Restart service
docker restart ai-engine
```

## Escalation Procedures

### Minor Issue (Response: 1-2 hours)

- Service operating with warnings
- Performance degradation (not error-related)
- Non-critical functionality impaired
- Notify team, document issue

### Major Issue (Response: 15 minutes)

- Service degraded or slow
- High error rate (>5%)
- Intermittent failures
- Page on-call engineer

### Critical Issue (Response: 5 minutes)

- Service completely down
- Complete loss of functionality
- Security incident
- Execute incident response plan

## Contact Information

- **On-Call Engineer**: Escalation email or paging system
- **Engineering Team**: team@pyramidxc.com
- **Security Issues**: security@pyramidxc.com
- **Support Requests**: support@pyramidxc.com

## Documentation References

- [Deployment Guide](DEPLOYMENT.md) - Deployment procedures
- [Architecture](ARCHITECTURE.md) - System design
- [Development](DEVELOPMENT.md) - Development procedures
- [SUPPORT.md](../SUPPORT.md) - User support guide

---

Last updated: 2024
