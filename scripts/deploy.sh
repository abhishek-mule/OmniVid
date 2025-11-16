#!/bin/bash
# Deployment utility script for OmniVid production deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check available disk space (minimum 10GB)
    available_space=$(df . | awk 'NR==2 {print $4}')
    if [ "$available_space" -lt 10485760 ]; then  # 10GB in KB
        log_error "Insufficient disk space. At least 10GB required."
        exit 1
    fi
    
    # Check available memory (minimum 4GB)
    available_memory=$(free -m | awk 'NR==2{print $7}')
    if [ "$available_memory" -lt 4096 ]; then
        log_warn "Low memory detected. At least 4GB recommended for production."
    fi
    
    log_info "System requirements check passed."
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Create necessary directories
    mkdir -p data/{redis,postgres,output,assets,tmp,prometheus,grafana}
    mkdir -p logs/{api,celery,nginx,postgres}
    mkdir -p config/{nginx/ssl,prometheus,grafana}
    
    # Set proper permissions
    chmod 755 data/* logs/* config/*
    chmod 600 config/redis/redis.conf 2>/dev/null || true
    
    log_info "Environment setup completed."
}

deploy_production() {
    log_info "Starting production deployment..."
    
    # Stop existing services
    docker-compose -f docker-compose.prod.yml down || true
    
    # Build and start services
    docker-compose -f docker-compose.prod.yml build --no-cache
    docker-compose -f docker-compose.prod.yml up -d
    
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Run health checks
    check_health
    
    log_info "Production deployment completed."
}

check_health() {
    log_info "Running health checks..."
    
    # Check API health
    if curl -f -s http://localhost:8000/health > /dev/null; then
        log_info "✓ API service is healthy"
    else
        log_error "✗ API service is not responding"
        return 1
    fi
    
    # Check Frontend health
    if curl -f -s http://localhost:3000/api/health > /dev/null; then
        log_info "✓ Frontend service is healthy"
    else
        log_error "✗ Frontend service is not responding"
        return 1
    fi
    
    # Check WebSocket status
    if curl -f -s http://localhost/ws/status > /dev/null; then
        log_info "✓ WebSocket service is healthy"
    else
        log_warn "✗ WebSocket service is not responding"
    fi
    
    # Check database connection
    if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U omnivid > /dev/null; then
        log_info "✓ Database is healthy"
    else
        log_error "✗ Database is not responding"
        return 1
    fi
    
    # Check Redis connection
    if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null; then
        log_info "✓ Redis is healthy"
    else
        log_error "✗ Redis is not responding"
        return 1
    fi
    
    log_info "All health checks passed."
}

show_status() {
    log_info "OmniVid Service Status:"
    echo
    docker-compose -f docker-compose.prod.yml ps
    echo
    log_info "Access URLs:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - API: http://localhost:8000"
    echo "  - Flower (Celery): http://localhost:5555"
    echo "  - Grafana: http://localhost:3001"
    echo "  - Prometheus: http://localhost:9090"
}

show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        docker-compose -f docker-compose.prod.yml logs -f
    else
        docker-compose -f docker-compose.prod.yml logs -f "$service"
    fi
}

backup_data() {
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    log_info "Creating backup in $backup_dir..."
    
    # Database backup
    docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U omnivid omnivid > "$backup_dir/database.sql"
    
    # File storage backup
    tar -czf "$backup_dir/files.tar.gz" data/output data/assets
    
    log_info "Backup created in $backup_dir"
}

restore_data() {
    local backup_file=$1
    if [ -z "$backup_file" ] || [ ! -f "$backup_file" ]; then
        log_error "Please provide a valid backup file path"
        exit 1
    fi
    
    log_warn "This will restore data from $backup_file. Are you sure? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log_info "Restore cancelled."
        exit 0
    fi
    
    # Stop services
    docker-compose -f docker-compose.prod.yml down
    
    # Restore database
    if [[ "$backup_file" == *.sql ]]; then
        log_info "Restoring database..."
        docker-compose -f docker-compose.prod.yml up -d postgres
        sleep 10
        docker-compose -f docker-compose.prod.yml exec -T postgres psql -U omnivid omnivid < "$backup_file"
    fi
    
    # Start all services
    docker-compose -f docker-compose.prod.yml up -d
    
    log_info "Restore completed."
}

cleanup() {
    log_info "Cleaning up old containers and images..."
    
    # Remove stopped containers
    docker container prune -f
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    # Clean old log files
    find logs/ -name "*.log" -mtime +30 -delete 2>/dev/null || true
    
    log_info "Cleanup completed."
}

# Main script
case "${1:-deploy}" in
    "deploy")
        check_requirements
        setup_environment
        deploy_production
        show_status
        ;;
    "health")
        check_health
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "$2"
        ;;
    "backup")
        backup_data
        ;;
    "restore")
        restore_data "$2"
        ;;
    "cleanup")
        cleanup
        ;;
    "stop")
        log_info "Stopping OmniVid services..."
        docker-compose -f docker-compose.prod.yml down
        ;;
    "restart")
        log_info "Restarting OmniVid services..."
        docker-compose -f docker-compose.prod.yml restart
        ;;
    *)
        echo "Usage: $0 {deploy|health|status|logs [service]|backup|restore <backup_file>|cleanup|stop|restart}"
        echo
        echo "Commands:"
        echo "  deploy      - Full production deployment"
        echo "  health      - Run health checks"
        echo "  status      - Show service status"
        echo "  logs        - Show logs (optionally specify service)"
        echo "  backup      - Create data backup"
        echo "  restore     - Restore from backup"
        echo "  cleanup     - Clean up old containers and logs"
        echo "  stop        - Stop all services"
        echo "  restart     - Restart all services"
        exit 1
        ;;
esac