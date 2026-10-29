from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .models import Patient
from .serializers import PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Patient management:
    - POST /api/patients/ - Add a new patient (Authenticated users only)
    - GET /api/patients/ - Retrieve all patients created by the authenticated user
    - GET /api/patients/<id>/ - Get details of a specific patient
    - PUT /api/patients/<id>/ - Update patient details
    - PATCH /api/patients/<id>/ - Partial update patient details
    - DELETE /api/patients/<id>/ - Delete a patient record
    """
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            # Staff can see all or filter by query param if desired
            return Patient.objects.all().order_by('-created_at')
        return Patient.objects.filter(created_by=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": f"Patient '{instance.name}' (ID: {instance.id}) deleted successfully."},
            status=status.HTTP_200_OK
        )
