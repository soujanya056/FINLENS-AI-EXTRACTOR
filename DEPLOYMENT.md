# Bank Statement OCR Extractor - Deployment Guide

## 🚀 Deployment Options

### Option 1: Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask app
python app.py
```

### Option 2: Docker (Recommended)

#### Build and Run with Docker
```bash
# Build image
docker build -t finlens-ocr:latest .

# Run container
docker run -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  --name finlens-ocr \
  finlens-ocr:latest
```

#### Docker Compose (Full Stack)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f ocr-backend

# Stop services
docker-compose down
```

### Option 3: Cloud Deployment

#### 🌐 **Heroku Deployment**

1. **Install Heroku CLI**
```bash
curl https://cli.heroku.com/install.sh | sh
```

2. **Login and Create App**
```bash
heroku login
heroku create finlens-ocr
```

3. **Add Buildpacks**
```bash
heroku buildpacks:add --index 1 https://github.com/heroku-community/apt-buildpack.git
heroku buildpacks:add --index 2 heroku/python

# Create Aptfile for system dependencies
echo "tesseract-ocr" > Aptfile
git add Aptfile
```

4. **Deploy**
```bash
git push heroku main
```

#### ☁️ **AWS Deployment (Elastic Beanstalk)**

1. **Install EB CLI**
```bash
pip install awsebcli
```

2. **Initialize**
```bash
eb init -p python-3.9 finlens-ocr --region us-east-1
```

3. **Create Environment**
```bash
eb create production-env
```

4. **Deploy**
```bash
eb deploy
```

5. **View Logs**
```bash
eb logs
```

#### 🐳 **Google Cloud Run**

1. **Setup**
```bash
gcloud auth login
gcloud config set project finlens-ocr
```

2. **Deploy**
```bash
gcloud run deploy finlens-ocr \
  --source . \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --timeout 3600 \
  --set-env-vars FLASK_ENV=production
```

#### 🎯 **Azure Container Instances**

1. **Build and Push to ACR**
```bash
az acr build --registry finlensocr --image finlens-ocr:latest .
```

2. **Deploy Container**
```bash
az container create \
  --resource-group finlens-rg \
  --name finlens-ocr \
  --image finlensocr.azurecr.io/finlens-ocr:latest \
  --cpu 2 \
  --memory 2 \
  --ports 5000 \
  --environment-variables FLASK_ENV=production
```

### Option 4: Kubernetes Deployment

#### Create `k8s-deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: finlens-ocr
spec:
  replicas: 3
  selector:
    matchLabels:
      app: finlens-ocr
  template:
    metadata:
      labels:
        app: finlens-ocr
    spec:
      containers:
      - name: ocr-backend
        image: finlens-ocr:latest
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: finlens-ocr-service
spec:
  selector:
    app: finlens-ocr
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

#### Deploy to Kubernetes
```bash
kubectl apply -f k8s-deployment.yaml
kubectl get services
```

## 📋 Prerequisites for Each Platform

### Heroku
- [ ] Heroku CLI installed
- [ ] Git repository
- [ ] Heroku account
- [ ] Aptfile for system dependencies

### AWS Elastic Beanstalk
- [ ] AWS CLI configured
- [ ] Elastic Beanstalk CLI
- [ ] IAM credentials with EB permissions
- [ ] `.elasticbeanstalk/config.yml`

### Google Cloud Run
- [ ] Google Cloud SDK
- [ ] Project with billing enabled
- [ ] Docker image or source code access

### Azure
- [ ] Azure CLI
- [ ] Container Registry
- [ ] Resource Group

### Kubernetes
- [ ] kubectl installed
- [ ] Kubernetes cluster access
- [ ] Container registry access

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```env
FLASK_ENV=production
FLASK_DEBUG=0
MAX_CONTENT_LENGTH=52428800
UPLOAD_FOLDER=uploads
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png,tiff,bmp
```

### Deployment Checklist

- [ ] Install Python dependencies
- [ ] Configure environment variables
- [ ] Set up logging
- [ ] Configure upload directory
- [ ] Set up monitoring/alerts
- [ ] Configure backups
- [ ] SSL/TLS certificates
- [ ] Domain configuration
- [ ] Rate limiting
- [ ] Database (if needed)

## 📊 Performance Optimization

### For Production

1. **Use Gunicorn instead of Flask dev server**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. **Enable Caching**
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
```

3. **Load Balancing**
```bash
# docker-compose with multiple instances
docker-compose up -d --scale ocr-backend=3
```

4. **Database Connection Pooling**
- Use connection pools for database access
- Configure timeouts appropriately

## 🔒 Security Considerations

### Before Deployment

- [ ] Disable debug mode (`FLASK_DEBUG=0`)
- [ ] Use strong secret keys
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Validate all file uploads
- [ ] Sanitize user inputs
- [ ] Configure firewall rules
- [ ] Use environment variables for secrets
- [ ] Enable logging and monitoring

### SSL Certificate

#### Let's Encrypt (Free)
```bash
# Using Certbot with Nginx
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com
```

## 📈 Monitoring & Logging

### Suggested Tools

- **Monitoring**: Prometheus, New Relic, DataDog
- **Logging**: ELK Stack, Splunk, CloudWatch
- **Error Tracking**: Sentry, Rollbar

### Basic Health Check

```bash
curl -X GET http://localhost:5000/health
```

## 🚦 CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
          heroku_app_name: "finlens-ocr"
          heroku_email: ${{ secrets.HEROKU_EMAIL }}
```

## 🆘 Troubleshooting

### Container won't start
```bash
docker logs finlens-ocr
```

### High memory usage
- Reduce scale factor in preprocessing
- Limit concurrent requests
- Use smaller batch sizes

### OCR timeout
- Increase timeout values
- Use faster OCR mode
- Reduce image size

### Port already in use
```bash
# Find and stop process
lsof -i :5000
kill -9 <PID>
```

## 📞 Support Resources

- Docker Docs: https://docs.docker.com/
- Heroku Docs: https://devcenter.heroku.com/
- AWS Docs: https://docs.aws.amazon.com/
- GCP Docs: https://cloud.google.com/docs/
- Azure Docs: https://docs.microsoft.com/azure/

---

**Ready to deploy! Choose your platform and follow the steps above.** 🚀
