from django.core.management.base import BaseCommand
from django.utils import timezone
from labs.models import LabSession
from labs.services.container_runtime import runtime, RuntimeErrorException


class Command(BaseCommand):
    help = "Stop and remove expired lab sessions"

    def handle(self, *args, **options):
        sessions = LabSession.objects.filter(status="running", expires_at__lte=timezone.now())
        for session in sessions:
            try:
                runtime.stop_container(session.container_id)
                runtime.destroy_container(session.container_id)
            except RuntimeErrorException:
                pass
            session.mark_finished(status="expired")
        self.stdout.write(self.style.SUCCESS(f"Expired sessions cleaned: {sessions.count()}"))
