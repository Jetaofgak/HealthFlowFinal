# HealthFlow Deployment Script for Windows (PowerShell)
# Run with: powershell -ExecutionPolicy Bypass -File deploy.ps1

param(
    [string]$DockerUsername = "taoufikjeta",
    [string]$ImageTag = "latest"
)

# Configuration
$ComposeFile = "docker-compose.yml"

Write-Host "═══════════════════════════════════════=" -ForegroundColor Blue
Write-Host "🚀 HealthFlow Deployment Script" -ForegroundColor Blue
Write-Host "═══════════════════════════════════════=" -ForegroundColor Blue
Write-Host "Docker Username: $DockerUsername" -ForegroundColor Green
Write-Host "Image Tag: $ImageTag" -ForegroundColor Green
Write-Host "Compose File: $ComposeFile" -ForegroundColor Green
Write-Host "═══════════════════════════════════════=" -ForegroundColor Blue

# Check Docker
Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow

if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker found" -ForegroundColor Green

if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose is not installed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker Compose found" -ForegroundColor Green

# Set environment variables
$env:DOCKER_USERNAME = $DockerUsername
$env:IMAGE_TAG = $ImageTag

# Pull latest images
Write-Host "`n📥 Pulling latest Docker images..." -ForegroundColor Yellow
try {
    docker-compose -f $ComposeFile pull
} catch {
    Write-Host "⚠️ Failed to pull some images, will build locally" -ForegroundColor Yellow
}

# Stop existing containers
Write-Host "`n🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f $ComposeFile down 2>$null

# Start services
Write-Host "`n🚀 Starting HealthFlow services..." -ForegroundColor Yellow
docker-compose -f $ComposeFile up -d

# Wait for services
Write-Host "`n⏳ Waiting for services to start (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service status
Write-Host "`n📊 Checking service status..." -ForegroundColor Yellow
docker-compose -f $ComposeFile ps

# Health checks
Write-Host "`n🏥 Running health checks..." -ForegroundColor Yellow

$services = @{
    "API Gateway" = "http://localhost:8085/actuator/health"
    "Proxy FHIR" = "http://localhost:8081/actuator/health"
    "DeID Service" = "http://localhost:5000/api/v1/health"
    "Featurizer" = "http://localhost:5001/api/v1/health"
    "ML Predictor" = "http://localhost:5002/api/v1/health"
    "Score API" = "http://localhost:5003/health"
    "Audit Fairness" = "http://localhost:5004/api/v1/health"
    "Dashboard" = "http://localhost:3002"
}

$allHealthy = $true

foreach ($service in $services.GetEnumerator()) {
    try {
        $response = Invoke-WebRequest -Uri $service.Value -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $($service.Key): HEALTHY" -ForegroundColor Green
        } else {
            Write-Host "❌ $($service.Key): UNHEALTHY (HTTP $($response.StatusCode))" -ForegroundColor Red
            $allHealthy = $false
        }
    } catch {
        Write-Host "❌ $($service.Key): UNREACHABLE" -ForegroundColor Red
        $allHealthy = $false
    }
}

# PostgreSQL check
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.Connect("localhost", 5433)
    $tcpClient.Close()
    Write-Host "✅ PostgreSQL: HEALTHY" -ForegroundColor Green
} catch {
    Write-Host "❌ PostgreSQL: UNHEALTHY" -ForegroundColor Red
    $allHealthy = $false
}

# Summary
Write-Host "`n═══════════════════════════════════════=" -ForegroundColor Blue

if ($allHealthy) {
    Write-Host "✅ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "`nAll services are healthy and running" -ForegroundColor Green
    Write-Host "`n📱 Access the application:" -ForegroundColor Yellow
    Write-Host "  Dashboard:    http://localhost:3002" -ForegroundColor Blue
    Write-Host "  API Gateway:  http://localhost:8085" -ForegroundColor Blue
} else {
    Write-Host "⚠️ DEPLOYMENT COMPLETED WITH WARNINGS" -ForegroundColor Yellow
    Write-Host "`nSome services are not healthy" -ForegroundColor Red
    Write-Host "Check logs with: docker-compose logs" -ForegroundColor Yellow
}

Write-Host "═══════════════════════════════════════=" -ForegroundColor Blue
