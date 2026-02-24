import uuid
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import Lab, LabSession
from ..serializers import LabSessionSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_lab(request, lab_id):
    try:
        lab = Lab.objects.get(id=lab_id)
    except Lab.DoesNotExist:
        return Response({"error": "Lab not found"}, status=status.HTTP_404_NOT_FOUND)

    container_id = f"labex-{uuid.uuid4().hex[:12]}"

    session = LabSession.objects.create(
        user=request.user,
        lab=lab,
        container_id=container_id,
        status="running"
    )

    serializer = LabSessionSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
