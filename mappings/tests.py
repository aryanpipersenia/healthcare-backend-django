from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from doctors.models import Doctor
from patients.models import Patient
from .models import PatientDoctorMapping


class MappingAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='mapping.admin@hospital.com',
            name='Mapping Admin',
            password='Password123!'
        )
        self.client.force_authenticate(user=self.user)

        self.patient = Patient.objects.create(
            created_by=self.user,
            name='Arthur Dent',
            age=42,
            gender='Male',
            phone='4242424242'
        )

        self.doctor1 = Doctor.objects.create(
            name='Leonard McCoy',
            specialization='General Medicine',
            email='mccoy@enterprise.org',
            phone='1701111111',
            years_of_experience=25
        )

        self.doctor2 = Doctor.objects.create(
            name='Beverly Crusher',
            specialization='Neurology',
            email='crusher@enterprise.org',
            phone='1701222222',
            years_of_experience=20
        )

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/mappings/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_assign_doctor_to_patient_success(self):
        payload = {
            'patient': self.patient.id,
            'doctor': self.doctor1.id,
            'notes': 'Initial consultation for regular checkup.'
        }
        response = self.client.post('/api/mappings/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['mapping']['patient'], self.patient.id)
        self.assertEqual(response.data['mapping']['doctor'], self.doctor1.id)
        self.assertTrue(
            PatientDoctorMapping.objects.filter(patient=self.patient, doctor=self.doctor1).exists()
        )

    def test_prevent_duplicate_mapping(self):
        # First assignment
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor1,
            assigned_by=self.user
        )
        # Attempt to assign the same doctor again to the same patient
        payload = {
            'patient': self.patient.id,
            'doctor': self.doctor1.id
        }
        response = self.client.post('/api/mappings/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_all_mappings(self):
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor1,
            assigned_by=self.user
        )
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor2,
            assigned_by=self.user
        )

        response = self.client.get('/api/mappings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_doctors_assigned_to_specific_patient(self):
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor1,
            notes='Cardiology follow-up',
            assigned_by=self.user
        )
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor2,
            notes='Neurology review',
            assigned_by=self.user
        )

        response = self.client.get(f'/api/mappings/{self.patient.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['patient_id'], self.patient.id)
        self.assertEqual(response.data['total_assigned_doctors'], 2)
        doctor_names = [d['doctor_name'] for d in response.data['doctors']]
        self.assertIn('Leonard McCoy', doctor_names)
        self.assertIn('Beverly Crusher', doctor_names)

    def test_remove_doctor_from_patient(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor1,
            assigned_by=self.user
        )
        response = self.client.delete(f'/api/mappings/{mapping.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PatientDoctorMapping.objects.filter(id=mapping.id).exists())
