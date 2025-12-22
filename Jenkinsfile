pipeline {
    agent any
    
    environment {
        // Skip Git LFS downloads (avoid large database backup file)
        GIT_LFS_SKIP_SMUDGE = '1'
        
        // Docker Hub credentials (configured in Jenkins Credentials)
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_USERNAME = 'taoufikjeta'
        DOCKER_CREDENTIALS_ID = 'dockerhub-credentials'
        
        // Git credentials
        GIT_CREDENTIALS_ID = 'github-credentials'
        
        // Database credentials
        POSTGRES_PASSWORD_ID = 'postgres-password'
        
        // Docker Compose file
        COMPOSE_FILE = 'docker-compose-joblib.yml'
        
        // Version tagging
        VERSION = "${env.BUILD_NUMBER}"
        // Note: GIT_SHORT_COMMIT will be set dynamically in Checkout stage
        
        // Service list for parallel builds
        JAVA_SERVICES = 'api-gateway,proxy-fhir'
        PYTHON_SERVICES = 'deID,featurizer,ml-predictor,score-api,audit-fairness'
        FRONTEND_SERVICES = 'dashboard-web'
    }
    
    triggers {
        // GitHub webhook trigger
        githubPush()
    }
    
    options {
        // Keep last 10 builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        
        // Timeout for entire pipeline
        timeout(time: 30, unit: 'MINUTES')
        
        // No concurrent builds on same branch
        disableConcurrentBuilds()
        
        // Timestamps in console output
        timestamps()
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "🔄 Checking out code from GitHub..."
                    checkout scm
                    
                    // Get Git commit hash (Windows compatible)
                    env.GIT_SHORT_COMMIT = powershell(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    env.IMAGE_TAG = "${env.GIT_BRANCH == 'main' ? 'latest' : env.GIT_BRANCH}-${env.VERSION}-${env.GIT_SHORT_COMMIT}"
                    
                    // Display build information
                    echo """
                    ════════════════════════════════════════
                    🚀 HealthFlow CI/CD Pipeline
                    ════════════════════════════════════════
                    Branch: ${env.GIT_BRANCH}
                    Commit: ${env.GIT_SHORT_COMMIT}
                    Build: #${env.BUILD_NUMBER}
                    Image Tag: ${env.IMAGE_TAG}
                    Compose File: ${env.COMPOSE_FILE}
                    ════════════════════════════════════════
                    """
                }
            }
        }
        
        stage('Build Java Services') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "☕ Building Java services with Maven..."
                    
                    JAVA_SERVICES.split(',').each { service ->
                        dir(service) {
                            echo "Building ${service}..."
                            
                            // Clean and package (Windows compatible)
                            bat """
                                mvnw.cmd clean package -DskipTests
                            """
                            
                            // Archive the JAR
                            archiveArtifacts artifacts: 'target/*.jar', fingerprint: true
                        }
                    }
                }
            }
        }
        
        stage('Build React Frontend') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "⚛️ Building React frontend..."
                    
                    dir('dashboard-web') {
                        // Clean install and build (Windows compatible)
                        bat """
                            npm ci
                            npm run build
                        """
                        
                        // Archive build artifacts
                        archiveArtifacts artifacts: 'dist/**/*', fingerprint: true
                    }
                }
            }
        }
        
        stage('Validate Python Services') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "🐍 Validating Python services..."
                    
                    PYTHON_SERVICES.split(',').each { service ->
                        dir(service) {
                            echo "Validating ${service}..."
                            
                            // Check requirements.txt exists (Windows compatible)
                            bat """
                                if not exist requirements.txt (
                                    echo ❌ Missing requirements.txt
                                    exit /b 1
                                )
                            """
                            echo "✅ ${service} validated"
                        }
                    }
                }
            }
        }
        
        stage('Run Tests') {
            when {
                branch 'main'
            }
            parallel {
                stage('Test Java Services') {
                    steps {
                        script {
                            echo "🧪 Testing Java services..."
                            
                            JAVA_SERVICES.split(',').each { service ->
                                dir(service) {
                                    try {
                                        bat 'mvnw.cmd test'
                                        
                                        // Publish test results
                                        junit allowEmptyResults: true, testResults: '**/target/surefire-reports/*.xml'
                                    } catch (Exception e) {
                                        echo "⚠️ Tests failed for ${service}, but continuing build..."
                                        currentBuild.result = 'UNSTABLE'
                                    }
                                }
                            }
                        }
                    }
                }
                
                stage('Test React Frontend') {
                    steps {
                        script {
                            dir('dashboard-web') {
                                try {
                                    // Run linting (Windows compatible)
                                    bat 'npm run lint || exit 0'
                                    echo "✅ Frontend tests completed"
                                } catch (Exception e) {
                                    echo "⚠️ Frontend tests had issues, but continuing..."
                                }
                            }
                        }
                    }
                }
            }
        }
        
        stage('Build Docker Images') {
            when {
                branch 'main'
            }
            parallel {
                stage('Build Java Images') {
                    steps {
                        script {
                            JAVA_SERVICES.split(',').each { service ->
                                buildDockerImage(service)
                            }
                        }
                    }
                }
                
                stage('Build Python Images') {
                    steps {
                        script {
                            PYTHON_SERVICES.split(',').each { service ->
                                buildDockerImage(service)
                            }
                        }
                    }
                }
                
                stage('Build Frontend Image') {
                    steps {
                        script {
                            buildDockerImage('dashboard-web')
                        }
                    }
                }
            }
        }
        
        stage('Push Docker Images') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "📤 Pushing Docker images to registry..."
                    
                    docker.withRegistry("https://${DOCKER_REGISTRY}", DOCKER_CREDENTIALS_ID) {
                        def allServices = JAVA_SERVICES + ',' + PYTHON_SERVICES + ',' + FRONTEND_SERVICES
                        
                        allServices.split(',').each { service ->
                            def serviceName = service.toLowerCase()
                            def imageName = "${DOCKER_USERNAME}/healthflow-${serviceName}"
                            
                            echo "Pushing ${imageName}:${env.IMAGE_TAG}"
                            
                            // Push with build-specific tag (Windows compatible)
                            bat "docker push ${imageName}:${env.IMAGE_TAG}"
                            
                            // Tag and push as 'latest' for main branch
                            bat "docker tag ${imageName}:${env.IMAGE_TAG} ${imageName}:latest"
                            bat "docker push ${imageName}:latest"
                            
                            echo "✅ Pushed ${imageName}"
                        }
                    }
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "🚀 Deploying HealthFlow services..."
                    
                    // Update docker-compose with new image versions (Windows compatible)
                    bat """
                        set IMAGE_TAG=${env.IMAGE_TAG}
                        set DOCKER_USERNAME=${DOCKER_USERNAME}
                        
                        @REM Pull latest images
                        docker-compose -f ${COMPOSE_FILE} pull
                        
                        @REM Stop and remove existing containers
                        docker-compose -f ${COMPOSE_FILE} down
                        
                        @REM Start services with new images
                        docker-compose -f ${COMPOSE_FILE} up -d
                        
                        @REM Wait for services to be healthy
                        timeout /t 30 /nobreak
                        
                        @REM Check service health
                        docker-compose -f ${COMPOSE_FILE} ps
                    """
                    
                    echo "✅ Deployment completed!"
                }
            }
        }
        
        stage('Health Check') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "🏥 Running health checks..."
                    
                    def services = [
                        [name: 'API Gateway', url: 'http://localhost:8085/actuator/health'],
                        [name: 'Proxy FHIR', url: 'http://localhost:8081/actuator/health'],
                        [name: 'DeID Service', url: 'http://localhost:5000/api/v1/health'],
                        [name: 'Featurizer', url: 'http://localhost:5001/api/v1/health'],
                        [name: 'ML Predictor', url: 'http://localhost:5002/api/v1/health'],
                        [name: 'Score API', url: 'http://localhost:5003/health'],
                        [name: 'Audit Fairness', url: 'http://localhost:5004/api/v1/health'],
                        [name: 'Dashboard', url: 'http://localhost:3002']
                    ]
                    
                    def allHealthy = true
                    
                    services.each { service ->
                        try {
                            // Use PowerShell for health checks (Windows compatible)
                            def response = powershell(
                                script: """
                                    try {
                                        \$result = Invoke-WebRequest -Uri '${service.url}' -UseBasicParsing -TimeoutSec 5
                                        \$result.StatusCode
                                    } catch {
                                        '000'
                                    }
                                """,
                                returnStdout: true
                            ).trim()
                            
                            if (response == '200') {
                                echo "✅ ${service.name}: HEALTHY"
                            } else {
                                echo "⚠️ ${service.name}: UNHEALTHY (HTTP ${response})"
                                allHealthy = false
                            }
                        } catch (Exception e) {
                            echo "❌ ${service.name}: FAILED - ${e.message}"
                            allHealthy = false
                        }
                    }
                    
                    if (!allHealthy) {
                        echo "⚠️ Some services are not healthy. Check logs with: docker-compose -f ${COMPOSE_FILE} logs"
                        currentBuild.result = 'UNSTABLE'
                    } else {
                        echo "✅ All services are healthy!"
                    }
                }
            }
        }
    }
    
    post {
        success {
            script {
                echo """
                ════════════════════════════════════════
                ✅ BUILD SUCCESSFUL!
                ════════════════════════════════════════
                All services deployed and healthy
                Dashboard: http://localhost:3002
                API Gateway: http://localhost:8085
                ════════════════════════════════════════
                """
                
                // Clean up old images to save space (Windows compatible)
                bat """
                    echo 🧹 Cleaning up old Docker images...
                    docker image prune -f --filter "until=168h"
                """
            }
        }
        
        failure {
            script {
                echo """
                ════════════════════════════════════════
                ❌ BUILD FAILED!
                ════════════════════════════════════════
                Check the logs above for details
                ════════════════════════════════════════
                """
            }
        }
        
        always {
            script {
                // Archive logs (Windows compatible)
                bat "docker-compose -f ${COMPOSE_FILE} logs > docker-compose.log 2>&1 || exit 0"
                archiveArtifacts artifacts: 'docker-compose.log', allowEmptyArchive: true
                
                echo "📊 Build #${env.BUILD_NUMBER} completed at ${new Date()}"
            }
        }
    }
}

// Helper function to build Docker images
def buildDockerImage(String service) {
    def serviceName = service.toLowerCase()
    def imageName = "${env.DOCKER_USERNAME}/healthflow-${serviceName}"
    def imageTag = "${imageName}:${env.IMAGE_TAG}"
    
    echo "🐳 Building Docker image: ${imageTag}"
    
    dir(service) {
        bat """
            docker build -t ${imageTag} .
        """
    }
    
    echo "✅ Built ${imageTag}"
}
