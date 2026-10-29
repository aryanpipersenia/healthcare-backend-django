from rest_framework import serializers

from doctors.models import Doctor
from doctors.serializers import DoctorSerializer
from patients.models import Patient
from patients.serializers import PatientSerializer
from .models import PatientDoctorMapping


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and retrieving Patient-Doctor mappings.
    Supports writing primary keys and reading detailed nested info.
    """
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())

    # Read-only convenience fields
    patient_name = serializers.ReadOnlyField(source='patient.name')
    doctor_name = serializers.ReadOnlyField(source='doctor.name')
    doctor_specialization = serializers.ReadOnlyField(source='doctor.specialization')
    assigned_by_name = serializers.ReadOnlyField(source='assigned_by.name')

    # Nested full details
    patient_details = PatientSerializer(source='patient', read_only=True)
    doctor_details = DoctorSerializer(source='doctor', read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = [
            'id',
            'patient',
            'patient_name',
            'patient_details',
            'doctor',
            'doctor_name',
            'doctor_specialization',
            'doctor_details',
            'assigned_at',
            'notes',
            'assigned_by',
            'assigned_by_name',
        ]
        read_only_fields = ['id', 'assigned_at', 'assigned_by', 'assigned_by_name']

    def validate(self, attrs):
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')
        request = self.context.get('request')

        # Ownership validation: Patient must belong to the user unless staff
        if request and request.user and not (request.user.is_staff or request.user.is_superuser):
            if patient.created_by != request.user:
                raise serializers.ValidationError(
                    {"patient": "You are not authorized to assign doctors to a patient created by another user."}
                )

        # Duplicate mapping validation
        duplicate_check = PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor)
        if self.instance:
            duplicate_check = duplicate_check.exclude(pk=self.instance.pk)

        if duplicate_check.exists():
            raise serializers.ValidationError(
                {"detail": f"Doctor '{doctor.name}' is already assigned to Patient '{patient.name}'."}
            )

        return attrs


class DoctorAssignmentDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for listing doctors assigned to a specific patient.
    """
    mapping_id = serializers.ReadOnlyField(source='id')
    doctor_id = serializers.ReadOnlyField(source='doctor.id')
    doctor_name = serializers.ReadOnlyField(source='doctor.name')
    specialization = serializers.ReadOnlyField(source='doctor.specialization')
    email = serializers.ReadOnlyField(source='doctor.email')
    phone = serializers.ReadOnlyField(source='doctor.phone')
    years_of_experience = serializers.ReadOnlyField(source='doctor.years_of_experience')
    department = serializers.ReadOnlyField(source='doctor.department')

    class Meta:
        model = PatientDoctorMapping
        fields = [
            'mapping_id',
            'doctor_id',
            'doctor_name',
            'specialization',
            'email',
            'phone',
            'years_of_experience',
            'department',
            'assigned_at',
            'notes',
        ]
