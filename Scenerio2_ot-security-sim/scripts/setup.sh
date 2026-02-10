#!/bin/bash
# OT Security Simulation - Setup and Deployment Script

set -e

echo "=========================================="
echo "  OT Security Simulation Setup"
echo "  Profinet IDS with Docker"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Please install Docker first: https://docs.docker.com/engine/install/ubuntu/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose is not installed"
    echo "Please install Docker Compose"
    exit 1
fi

echo "✓ Docker is installed"
echo "✓ Docker Compose is installed"
echo ""

# Create log directories
echo "Creating log directories..."
mkdir -p logs/{plc,hmi,ids}
chmod -R 777 logs/

# Build containers
echo ""
echo "Building Docker containers..."
echo "This may take a few minutes..."
echo ""

docker-compose build

echo ""
echo "✓ Containers built successfully"
echo ""

# Start containers
echo "Starting OT Security Simulation..."
echo ""

docker-compose up -d

echo ""
echo "Waiting for services to initialize..."
sleep 10

# Check container status
echo ""
echo "Container Status:"
echo "─────────────────────────────────────────"
docker-compose ps
echo ""

# Display network information
echo "Network Configuration:"
echo "─────────────────────────────────────────"
docker network inspect ot-security-simulation_ot_network | grep -A 10 "Containers"
echo ""

echo "=========================================="
echo "  OT Security Simulation is Running!"
echo "=========================================="
echo ""
echo "Access containers:"
echo "  - PLC:  docker exec -it ot_plc bash"
echo "  - HMI:  docker exec -it ot_hmi bash"
echo "  - IDS:  docker exec -it ot_ids bash"
echo ""
echo "Monitor IDS alerts:"
echo "  docker exec -it ot_ids python3 /app/monitor.py"
echo ""
echo "View logs:"
echo "  - PLC:  tail -f logs/plc/plc.log"
echo "  - HMI:  tail -f logs/hmi/hmi.log"
echo "  - IDS:  tail -f logs/suricata/eve.json"
echo ""
echo "To stop: docker-compose down"
echo ""
