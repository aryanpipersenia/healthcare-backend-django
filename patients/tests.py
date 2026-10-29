from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from .models import Patient


class PatientAPITests(APITestCase):
    def setUp(self):
        # Create primary test user
        self.user1 = User.objects.create_user(
            email='user1@hospital.com',
            name='User One',
            password='Password123!'
        )
        # Create second user to test ownership isolation
        self.user2 = User.objects.create_user(
            email='user2@hospital.com',
            name='User Two',
            password='Password123!'
        )

        # Authenticate user 1
        self.client.force_authenticate(user=self.user1)

        self.patient_payload = {
            'name': 'John Doe',
            'age': 45,
            'gender': 'Male',
            'phone': '1234567890',
            'email': 'john.doe@example.com',
            'address': '123 Health Ave, Metropolis',
            'medical_history': 'Hypertension and seasonal allergies.'
        }

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/patients/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_patient_success(self):
        response = self.client.post('/api/patients/', self.patient_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'John Doe')
        self.assertEqual(response.data['created_by'], self.user1.id)

    def test_retrieve_only_user_created_patients(self):
        # Patient for user1
        Patient.objects.create(
            created_by=self.user1,
            name='Patient One',
            age=30,
            gender='Female',
            phone='1112223333'
        )
        # Patient for user2
        Patient.objects.create(
            created_by=self.user2,
            name='Patient Two',
            age=40,
            gender='Male',
            phone='4445556666'
        )

        response = self.client.get('/api/patients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # User 1 should only see 1 patient
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Patient One')

    def test_get_patient_details(self):
        patient = Patient.objects.create(
            created_by=self.user1,
            name='Jane Smith',
            age=28,
            gender='Female',
            phone='9876543210'
        )
        response = self.client.get(f'/api/patients/{patient.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Jane Smith')

    def test_update_patient_details(self):
        patient = Patient.objects.create(
            created_by=self.user1,
            name='Bob Brown',
            age=50,
            gender='Male',
            phone='5555555555'
        )
        update_data = {
            'name': 'Bob Brown Jr.',
            'age': 51,
            'gender': 'Male',
            'phone': '5555555555',
            'medical_history': 'Updated condition report'
        }
        response = self.client.put(f'/api/patients/{patient.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Bob Brown Jr.')
        self.assertEqual(response.data['age'], 51)

    def test_delete_patient_record(self):
        patient = Patient.objects.create(
            created_by=self.user1,
            name='Temporary Patient',
            age=22,
            gender='Other',
            phone='9998887777'
        )
        response = self.client.delete(f'/api/patients/{patient.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Patient.objects.filter(id=patient.id).exists())

    def test_cannot_access_other_users_patient(self):
        patient_user2 = Patient.objects.create(
            created_by=self.user2,
            name='User2 Secret Patient',
            age=35,
            gender='Female',
            phone='3332221111'
        )
        # User 1 attempts to access user 2's patient
        response = self.client.get(f'/api/patients/{patient_user2.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
