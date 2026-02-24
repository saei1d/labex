# LabEx - Interactive Programming Labs Platform

LabEx is a Django-based platform for interactive programming labs with Docker integration. Students can practice coding in isolated environments while their code is automatically validated.

## Features

- 🐚 **Docker Integration**: Each lab runs in an isolated container with VSCode-like interface
- 🧪 **Automated Testing**: Code submissions are automatically tested with pytest
- 📚 **Course Management**: Organize labs into courses and modules
- 📊 **Progress Tracking**: Monitor student progress and performance
- 🔐 **JWT Authentication**: Secure API with token-based authentication
- ⚡ **Background Tasks**: Celery for asynchronous code validation

## Architecture

### Core Components

1. **Accounts**: User management with custom User model
2. **Courses**: Course and module structure
3. **Labs**: Lab sections with Docker integration
4. **Progress**: User progress tracking
5. **Docker Manager**: Container lifecycle management
6. **Code Validator**: Automated code testing

### Models

- **User**: Custom user model with email-based authentication
- **Course/CourseModule**: Course structure
- **Lab/LabSection**: Lab content and sections
- **LabSession**: Container sessions for users
- **LabSubmission**: Code submissions
- **TestCase/TestResult**: Automated testing framework

## Setup Instructions

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Redis (for Celery)
- PostgreSQL

### Installation

1. **Clone and Setup**
   ```bash
   git clone <repository>
   cd labex
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirments.txt
   ```

3. **Start Services**
   ```bash
   docker-compose up -d
   ```

4. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Sample Data**
   ```bash
   python manage.py create_sample_data
   ```

6. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

7. **Start Celery Worker** (in separate terminal)
   ```bash
   celery -A labex worker -l info
   ```

### Docker Images

Build the Python lab image:
```bash
cd docker_images/python
docker build -t labex/python:latest .
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh

### Courses
- `GET /api/courses/` - List courses
- `GET /api/modules/` - List modules

### Labs
- `GET /api/labs/` - List labs
- `POST /api/labs/{id}/start/` - Start lab session
- `POST /api/labs/sessions/{id}/stop/` - Stop lab session
- `GET /api/labs/sessions/{id}/status/` - Session status

### Submissions
- `POST /api/submissions/submit_code/` - Submit code for validation
- `GET /api/submissions/{id}/results/` - Get validation results

## Usage Flow

1. **User Registration/Login**: Users create accounts or login with JWT tokens
2. **Course Selection**: Browse available courses and labs
3. **Start Lab**: Request a lab session → Docker container created
4. **Code Editor**: Access VSCode-like interface in browser
5. **Submit Code**: Submit solutions for automatic testing
6. **Get Results**: View test results and feedback
7. **Progress**: Track completion and move to next section

## Docker Integration

Each lab session creates a Docker container with:
- Code-server (VSCode in browser)
- Python runtime and testing tools
- Isolated file system
- Automatic cleanup after timeout

## Testing Framework

- **Pytest**: Automated test execution
- **Custom Test Cases**: Define tests per lab section
- **Real-time Feedback**: Immediate results to users
- **Score Tracking**: Points-based evaluation

## Security Features

- JWT-based authentication
- Container isolation
- Resource limits
- Automatic cleanup
- Input validation

## Development

### Adding New Labs

1. Create Lab and LabSection objects
2. Define TestCase objects with pytest code
3. Set appropriate docker_image
4. Add content in markdown format

### Custom Docker Images

Create custom Docker images in `docker_images/` directory with:
- Code-server installation
- Required runtime/tools
- Security configurations

## Monitoring

- Container health checks
- Resource usage monitoring
- Session lifecycle tracking
- Error logging

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## License

[Add your license here]

## Support

For issues and questions, please open an issue on GitHub.
