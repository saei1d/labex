#!/bin/bash

# LabEx Setup Script

echo "🚀 Setting up LabEx Platform..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirments.txt

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create sample data
echo "📚 Creating sample data..."
python manage.py create_sample_data

# Start Celery worker (in background)
echo "⚡ Starting Celery worker..."
celery -A labex worker -l info --detach

# Start Django server
echo "🌐 Starting Django development server..."
echo "📖 API Documentation: http://localhost:8000/swagger/"
echo "👤 Admin User: admin@labex.com / admin123"
echo "🎯 Ready to go! Access the app at http://localhost:8000"

python manage.py runserver
