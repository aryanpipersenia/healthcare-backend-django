from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from .models import Doctor


class DoctorAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='dr.admin@hospital.com',
            name='Hospital Admin',
            password='Password123!'
        )
        self.client.force_authenticate(user=self.user)

        self.doctor_payload = {
            'name': 'Gregory House',
            'specialization': 'Diagnostic Medicine',
            'email': 'g.house@princeton-plainsboro.org',
            'phone': '5551234567',
            'years_of_experience': 20,
            'department': 'Nephrology & Pathology'
        }

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/doctors/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_doctor_success(self):
        response = self.client.post('/api/doctors/', self.doctor_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Gregory House')
        self.assertEqual(response.data['specialization'], 'Diagnostic Medicine')

    def test_create_doctor_duplicate_email(self):
        self.client.post('/api/doctors/', self.doctor_payload)
        # Try creating again with duplicate email
        response = self.client.post('/api/doctors/', self.doctor_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_all_doctors(self):
        Doctor.objects.create(
            name='James Wilson',
            specialization='Oncology',
            email='j.wilson@hospital.com',
            phone='5551112222',
            years_of_experience=15
        )
        Doctor.objects.create(
            name='Lisa Cuddy',
            specialization='Endocrinology',
            email='l.cuddy@hospital.com',
            phone='5553334444',
            years_of_experience=18
        )
        response = self.client.get('/api/doctors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_doctor_details(self):
        doctor = Doctor.objects.create(
            name='Robert Chase',
            specialization='Surgery',
            email='r.chase@hospital.com',
            phone='5559998888',
            years_of_experience=10
        )
        response = self.client.get(f'/api/doctors/{doctor.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Robert Chase')
        self.assertEqual(response.data['specialization'], 'Surgery')

    def test_update_doctor_details(self):
        doctor = Doctor.objects.create(
            name='Allison Cameron',
            specialization='Immunology',
            email='a.cameron@hospital.com',
            phone='5557776666',
            years_of_experience=8
        )
        updated_data = {
            'name': 'Allison Cameron',
            'specialization': 'Senior Immunology',
            'email': 'a.cameron@hospital.com',
            'phone': '5557776666',
            'years_of_experience': 9
        }
        response = self.client.put(f'/api/doctors/{doctor.id}/', updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['specialization'], 'Senior Immunology')
        self.assertEqual(response.data['years_of_experience'], 9)

    def test_delete_doctor_record(self):
        doctor = Doctor.objects.create(
            name='Temporary Doctor',
            specialization='General',
            email='temp.doc@hospital.com',
            phone='5550001111',
            years_of_experience=1
        )
        response = self.client.delete(f'/api/doctors/{doctor.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Doctor.objects.filter(id=doctor.id).exists())
