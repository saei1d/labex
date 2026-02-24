import docker
import uuid
from datetime import datetime, timedelta
from labs.models import LabSession


class DockerManager:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            raise Exception(f"Cannot connect to Docker: {e}")

    def start_lab_session(self, user, lab):
        """Start a new lab session with a Docker container."""
        try:
            # Stop existing sessions for this user and lab
            self.stop_user_lab_sessions(user, lab)

            # Generate unique container name and access token
            container_name = f"labex_{user.id}_{lab.id}_{uuid.uuid4().hex[:8]}"
            access_token = uuid.uuid4().hex

            # Find an available port
            container_port = self._find_available_port()

            # Create and start container
            container = self.client.containers.run(
                lab.docker_image,
                name=container_name,
                ports={'8080/tcp': container_port},
                environment={
                    'PASSWORD': access_token,
                    'USER_ID': str(user.id),
                    'LAB_ID': str(lab.id)
                },
                volumes={
                    f'/tmp/labex_{user.id}_{lab.id}': {
                        'bind': '/home/coder/project',
                        'mode': 'rw'
                    }
                },
                detach=True,
                remove=False
            )

            # Create lab session record
            session = LabSession.objects.create(
                user=user,
                lab=lab,
                container_id=container.id,
                container_port=container_port,
                access_token=access_token,
                status='running',
                expires_at=datetime.now() + timedelta(hours=2)
            )

            return {
                'session_id': session.id,
                'container_url': f'http://localhost:{container_port}',
                'access_token': access_token,
                'expires_at': session.expires_at
            }

        except Exception as e:
            raise Exception(f"Failed to start lab session: {e}")

    def stop_lab_session(self, session):
        """Stop a lab session and remove the container."""
        try:
            if session.container_id:
                container = self.client.containers.get(session.container_id)
                container.stop()
                container.remove()
            
            session.status = 'stopped'
            session.ended_at = datetime.now()
            session.save()

        except docker.errors.NotFound:
            # Container already removed
            session.status = 'stopped'
            session.ended_at = datetime.now()
            session.save()
        except Exception as e:
            raise Exception(f"Failed to stop lab session: {e}")

    def stop_user_lab_sessions(self, user, lab=None):
        """Stop all running sessions for a user (optionally for a specific lab)."""
        sessions = LabSession.objects.filter(
            user=user,
            status='running'
        )
        
        if lab:
            sessions = sessions.filter(lab=lab)

        for session in sessions:
            try:
                self.stop_lab_session(session)
            except Exception:
                # Continue with other sessions even if one fails
                continue

    def get_container_logs(self, session):
        """Get logs from a container."""
        try:
            container = self.client.containers.get(session.container_id)
            return container.logs().decode('utf-8')
        except Exception as e:
            return f"Error getting logs: {e}"

    def execute_command_in_container(self, session, command):
        """Execute a command in the container."""
        try:
            container = self.client.containers.get(session.container_id)
            result = container.exec_run(command)
            return {
                'exit_code': result.exit_code,
                'output': result.output.decode('utf-8')
            }
        except Exception as e:
            return {
                'exit_code': -1,
                'output': f"Error executing command: {e}"
            }

    def _find_available_port(self):
        """Find an available port starting from 8081."""
        import socket
        for port in range(8081, 9081):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('localhost', port))
                sock.close()
                return port
            except OSError:
                continue
        raise Exception("No available ports found")

    def cleanup_expired_sessions(self):
        """Clean up expired lab sessions."""
        expired_sessions = LabSession.objects.filter(
            expires_at__lt=datetime.now(),
            status='running'
        )
        
        for session in expired_sessions:
            try:
                self.stop_lab_session(session)
            except Exception:
                continue
