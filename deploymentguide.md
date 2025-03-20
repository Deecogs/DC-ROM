# ROM Analysis System Deployment Guide

This guide walks through the steps to deploy the ROM Analysis System using Docker in both development and production environments.

## Prerequisites

- Docker and Docker Compose installed
- Git (optional)
- 2GB+ RAM and 2+ CPU cores recommended

## Quick Start

### Development Deployment

1. Clone the repository (or copy all files to your deployment folder)

```bash
git clone <repository-url>
cd rom-analysis-system
```

2. Build and start the containers

```bash
docker-compose up -d
```

3. Access the API

- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- WebSocket Demo: http://localhost:8000

### Production Deployment

For a production environment, use the full setup with Nginx:

1. Create necessary directories:

```bash
mkdir -p nginx/conf.d data static/css static/js
```

2. Copy the Nginx configuration:

```bash
# Copy to nginx/conf.d/rom.conf
cp nginx-conf.conf nginx/conf.d/rom.conf
```

3. Create a basic Nginx main configuration:

```bash
cat > nginx/nginx.conf << 'EOF'
user  nginx;
worker_processes  auto;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     on;
    keepalive_timeout  65;
    types_hash_max_size 2048;
    client_max_body_size 20M;

    gzip  on;
    gzip_disable "msie6";
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    include /etc/nginx/conf.d/*.conf;
}
EOF
```

4. Start the full stack:

```bash
docker-compose up -d
```

5. Access the API at http://localhost (port 80)

## Configuration Options

### Environment Variables

You can customize the deployment by setting environment variables in the docker-compose.yml file:

```yaml
environment:
  - ENVIRONMENT=production # production or development
  - LOG_LEVEL=info # debug, info, warning, error
  - MAX_WORKERS=4 # Number of worker processes
  - TIMEOUT=120 # Request timeout in seconds
```

### Resource Limits

Adjust resource limits in the docker-compose.yml file based on your server capabilities:

```yaml
deploy:
  resources:
    limits:
      cpus: "2" # Number of CPU cores
      memory: 2G # Memory limit
```

## Running Without Docker

If you prefer to run without Docker:

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the API server:

```bash
python run.py api
```

3. Or run the demo directly:

```bash
python run.py holistic
```

## Troubleshooting

### Container Fails to Start

Check the logs:

```bash
docker-compose logs rom-api
```

### Performance Issues

- Increase resource limits in docker-compose.yml
- Reduce model complexity for faster processing:

```bash
# Inside the container
holistic-demo --complexity 0
```

### WebSocket Connection Issues

- Check browser console for errors
- Ensure Nginx is configured correctly for WebSocket proxying
- Verify firewall settings allow WebSocket connections

## Security Considerations

For production deployments:

1. Use HTTPS (TLS/SSL) - configure Nginx with proper certificates
2. Implement authentication for API endpoints
3. Set up proper firewall rules
4. Consider using a reverse proxy like Traefik or HAProxy
5. Run regular security updates

## Updating

To update to a new version:

```bash
# Pull the latest code
git pull

# Rebuild and restart containers
docker-compose down
docker-compose build
docker-compose up -d
```

## Backup

Backup your data directory regularly:

```bash
tar -czf rom-data-backup-$(date +%Y%m%d).tar.gz data/
```
