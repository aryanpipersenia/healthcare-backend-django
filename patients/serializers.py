from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient model with validation and read-only ownership.
    """
    created_by_name = serializers.ReadOnlyField(source='created_by.name')
    created_by_email = serializers.ReadOnlyField(source='created_by.email')

    class Meta:
        model = Patient
        fields = [
            'id',
            'name',
            'age',
            'gender',
            'phone',
            'email',
            'address',
            'medical_history',
            'created_by',
            'created_by_name',
            'created_by_email',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_by_name', 'created_by_email', 'created_at', 'updated_at']

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Patient name cannot be blank.")
        return name

    def validate_age(self, value):
        if value < 0 or value > 150:
            raise serializers.ValidationError("Age must be between 0 and 150.")
        return value

    def validate_phone(self, value):
        phone = value.strip()
        if not phone:
            raise serializers.ValidationError("Phone number cannot be blank.")
        # Basic sanity check for numeric characters
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 7:
            raise serializers.ValidationError("Phone number must contain at least 7 digits.")
        return phone
