from celery import shared_task
from django.utils import timezone
from docker_manager.manager import DockerManager
from validators.code_validator import CodeValidator
from labs.models import LabSession, LabSubmission


@shared_task
def cleanup_expired_sessions():
    """Clean up expired lab sessions."""
    docker_manager = DockerManager()
    try:
        docker_manager.cleanup_expired_sessions()
        return f"Cleaned up expired sessions at {timezone.now()}"
    except Exception as e:
        return f"Error cleaning up sessions: {e}"


@shared_task
def validate_submission(submission_id):
    """Validate a code submission asynchronously."""
    try:
        submission = LabSubmission.objects.get(id=submission_id)
        validator = CodeValidator()
        result = validator.validate_submission(submission)
        
        # Update user progress if all tests passed
        if result['passed_all']:
            from progress.models import UserLabProgress
            progress, created = UserLabProgress.objects.get_or_create(
                user=submission.user,
                lab=submission.lab_section.lab,
                defaults={'completed': True, 'score': result['percentage']}
            )
            if not created:
                progress.completed = True
                progress.score = max(progress.score, result['percentage'])
                progress.save()
        
        return result
    except Exception as e:
        return f"Error validating submission {submission_id}: {e}"


@shared_task
def stop_lab_session(session_id):
    """Stop a lab session asynchronously."""
    try:
        session = LabSession.objects.get(id=session_id)
        docker_manager = DockerManager()
        docker_manager.stop_lab_session(session)
        return f"Stopped session {session_id}"
    except Exception as e:
        return f"Error stopping session {session_id}: {e}"


@shared_task
def monitor_container_health():
    """Monitor health of running containers."""
    docker_manager = DockerManager()
    try:
        running_sessions = LabSession.objects.filter(status='running')
        unhealthy_count = 0
        
        for session in running_sessions:
            try:
                # Check if container is still running
                container = docker_manager.client.containers.get(
                    session.container_id
                )
                container.reload()
                
                if container.status != 'running':
                    docker_manager.stop_lab_session(session)
                    unhealthy_count += 1
                    
            except Exception:
                # Container doesn't exist, stop the session
                docker_manager.stop_lab_session(session)
                unhealthy_count += 1
        
        return f"Monitored {running_sessions.count()} sessions, "
        f"cleaned up {unhealthy_count} unhealthy containers"
        
    except Exception as e:
        return f"Error monitoring containers: {e}"
