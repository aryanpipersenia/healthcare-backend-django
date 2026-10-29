from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from patients.models import Patient
from .models import PatientDoctorMapping
from .serializers import DoctorAssignmentDetailSerializer, PatientDoctorMappingSerializer


class MappingListCreateView(APIView):
    """
    POST /api/mappings/ - Assign a doctor to a patient.
    GET /api/mappings/ - Retrieve all patient-doctor mappings.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_staff or user.is_superuser:
            mappings = PatientDoctorMapping.objects.all().select_related('patient', 'doctor', 'assigned_by')
        else:
            mappings = PatientDoctorMapping.objects.filter(
                patient__created_by=user
            ).select_related('patient', 'doctor', 'assigned_by')

        serializer = PatientDoctorMappingSerializer(mappings, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PatientDoctorMappingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            mapping = serializer.save(assigned_by=request.user)
            return Response(
                {
                    "message": "Doctor assigned to patient successfully.",
                    "mapping": PatientDoctorMappingSerializer(mapping, context={'request': request}).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MappingDetailOrPatientDoctorsView(APIView):
    """
    GET /api/mappings/<patient_id>/ - Get all doctors assigned to a specific patient.
    DELETE /api/mappings/<id>/ - Remove a doctor from a patient (delete mapping by mapping ID).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, identifier):
        user = request.user

        # Try to find patient by ID first to satisfy:
        # GET /api/mappings/<patient_id>/ - Get all doctors assigned to a specific patient
        patient = Patient.objects.filter(pk=identifier).first()
        if patient:
            # Check ownership
            if not (user.is_staff or user.is_superuser) and patient.created_by != user:
                return Response(
                    {"error": "You do not have permission to view doctors for this patient."},
                    status=status.HTTP_403_FORBIDDEN
                )

            mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('doctor')
            doctors_data = DoctorAssignmentDetailSerializer(mappings, many=True).data

            return Response(
                {
                    "patient_id": patient.id,
                    "patient_name": patient.name,
                    "total_assigned_doctors": len(doctors_data),
                    "doctors": doctors_data
                },
                status=status.HTTP_200_OK
            )

        # Fallback: if not found as patient_id, check if identifier is a mapping ID
        mapping = PatientDoctorMapping.objects.filter(pk=identifier).first()
        if mapping:
            if not (user.is_staff or user.is_superuser) and mapping.patient.created_by != user:
                return Response(
                    {"error": "You do not have permission to view this mapping."},
                    status=status.HTTP_403_FORBIDDEN
                )
            return Response(
                PatientDoctorMappingSerializer(mapping, context={'request': request}).data,
                status=status.HTTP_200_OK
            )

        return Response(
            {"error": f"No patient or mapping found with ID '{identifier}'."},
            status=status.HTTP_404_NOT_FOUND
        )

    def delete(self, request, identifier):
        """
        DELETE /api/mappings/<id>/ - Remove a doctor from a patient (by mapping ID).
        """
        user = request.user
        mapping = PatientDoctorMapping.objects.filter(pk=identifier).first()

        if not mapping:
            return Response(
                {"error": f"Mapping with ID '{identifier}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Ensure user owns the patient in this mapping
        if not (user.is_staff or user.is_superuser) and mapping.patient.created_by != user:
            return Response(
                {"error": "You do not have permission to delete this mapping."},
                status=status.HTTP_403_FORBIDDEN
            )

        patient_name = mapping.patient.name
        doctor_name = mapping.doctor.name
        mapping_id = mapping.id
        mapping.delete()

        return Response(
            {
                "message": f"Successfully unassigned Dr. {doctor_name} from Patient {patient_name}.",
                "deleted_mapping_id": mapping_id
            },
            status=status.HTTP_200_OK
        )


class PatientDoctorsListView(APIView):
    """
    Dedicated endpoint:
    GET /api/mappings/patient/<patient_id>/
    Get all doctors assigned to a specific patient.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, patient_id):
        user = request.user
        patient = get_object_or_404(Patient, pk=patient_id)

        if not (user.is_staff or user.is_superuser) and patient.created_by != user:
            return Response(
                {"error": "You do not have permission to view doctors for this patient."},
                status=status.HTTP_403_FORBIDDEN
            )

        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('doctor')
        doctors_data = DoctorAssignmentDetailSerializer(mappings, many=True).data

        return Response(
            {
                "patient_id": patient.id,
                "patient_name": patient.name,
                "total_assigned_doctors": len(doctors_data),
                "doctors": doctors_data
            },
            status=status.HTTP_200_OK
        )
