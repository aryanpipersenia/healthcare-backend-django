from rest_framework import serializers

from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for Doctor model with validation.
    """
    created_by_name = serializers.ReadOnlyField(source='created_by.name')

    class Meta:
        model = Doctor
        fields = [
            'id',
            'name',
            'specialization',
            'email',
            'phone',
            'years_of_experience',
            'department',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_by_name', 'created_at', 'updated_at']

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Doctor name cannot be blank.")
        return name

    def validate_specialization(self, value):
        spec = value.strip()
        if not spec:
            raise serializers.ValidationError("Specialization cannot be blank.")
        return spec

    def validate_email(self, value):
        normalized = value.strip().lower()
        # On update, allow current instance's email
        query = Doctor.objects.filter(email__iexact=normalized)
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise serializers.ValidationError("A doctor with this email already exists.")
        return normalized

    def validate_phone(self, value):
        phone = value.strip()
        if not phone:
            raise serializers.ValidationError("Phone number cannot be blank.")
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 7:
            raise serializers.ValidationError("Phone number must contain at least 7 digits.")
        return phone
