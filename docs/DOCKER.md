# Docker Setup - Sprint 1 Day 3

## Quick Start

### Option 1: Docker Compose (Recommended)
```bash
# Start the application
docker compose up -d

# View logs
docker compose logs -f

# Stop the application  
docker compose down
```

Application will be available at: http://localhost:8504

### Option 2: Manual Docker Run
```bash
# Build the image
docker build -t ukge-simulator .

# Run the container
docker run -d --name ukge-app -p 8501:8501 ukge-simulator

# Check health
curl http://localhost:8501/_stcore/health

# Stop and remove
docker stop ukge-app && docker rm ukge-app
```

## Testing

Run the comprehensive test suite:
```bash
./test_docker_setup.sh
```

This script validates:
- Docker image build
- Container startup
- Health check endpoint
- Main application response
- Docker compose deployment

## Development Mode

For development with live code reloading:
```bash
docker compose --profile dev up
```

This runs on port 8502 with live code mounting.

## Health Monitoring

The application includes built-in health checks:
- **Endpoint**: `/_stcore/health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3

## Day 3 Achievements ✅

- ✅ Production-ready Docker containerization
- ✅ Automated testing pipeline
- ✅ Docker compose orchestration
- ✅ Health monitoring and checks
- ✅ Development workflow optimization
- ✅ Comprehensive documentation

**Ready for Day 4**: Streamlit Cloud deployment and domain configuration.
