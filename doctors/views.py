from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .models import Doctor
from .serializers import DoctorSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Doctor management:
    - POST /api/doctors/ - Add a new doctor (Authenticated users only)
    - GET /api/doctors/ - Retrieve all doctors
    - GET /api/doctors/<id>/ - Get details of a specific doctor
    - PUT /api/doctors/<id>/ - Update doctor details
    - PATCH /api/doctors/<id>/ - Partial update doctor details
    - DELETE /api/doctors/<id>/ - Delete a doctor record
    """
    queryset = Doctor.objects.all().order_by('-created_at')
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": f"Doctor '{instance.name}' (ID: {instance.id}) deleted successfully."},
            status=status.HTTP_200_OK
        )
