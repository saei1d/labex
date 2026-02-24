@echo off
echo 🚀 Setting up LabEx Platform...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirments.txt

REM Start services
echo 🐳 Starting Docker services...
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak

REM Run migrations
echo 🗄️ Running database migrations...
python manage.py makemigrations
python manage.py migrate

REM Create sample data
echo 📚 Creating sample data...
python manage.py create_sample_data

echo 🌐 Starting Django development server...
echo 📖 API Documentation: http://localhost:8000/swagger/
echo 👤 Admin User: admin@labex.com / admin123
echo 🎯 Ready to go! Access at http://localhost:8000
echo.
echo To start Celery worker in another terminal:
echo venv\Scripts\activate.bat
echo celery -A labex worker -l info
echo.

python manage.py runserver
