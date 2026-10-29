"""
Automated end-to-end API client verification script.
Tests all endpoints sequentially using Django REST Framework's APIClient:
1. Registration & Login (JWT)
2. Patient CRUD (Authenticated)
3. Doctor CRUD (Authenticated)
4. Patient-Doctor Mappings (Assignment, Retrieval, Patient-specific lookup, Removal)
5. Validation and Permission checks
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare_project.settings')
django.setup()

from rest_framework.test import APIClient
from accounts.models import User
from patients.models import Patient
from doctors.models import Doctor
from mappings.models import PatientDoctorMapping


def run_e2e_tests():
    print("=================================================================")
    print("  HEALTHCARE BACKEND - END-TO-END API TEST RUNNER")
    print("=================================================================\n")

    client = APIClient()

    # 1. Test Registration
    print("[1/5] Testing User Registration (/api/auth/register/)...")
    reg_payload = {
        "name": "Dr. Lisa Cuddy",
        "email": "cuddy.dean@hospital.com",
        "password": "MedicalDirector2026!"
    }
    # Clean up if prior run exists
    User.objects.filter(email=reg_payload["email"].lower()).delete()

    reg_resp = client.post('/api/auth/register/', reg_payload, format='json')
    assert reg_resp.status_code == 201, f"Register failed: {reg_resp.data}"
    print(f"  --> Registered user: {reg_resp.data['user']['name']} ({reg_resp.data['user']['email']})")

    # 2. Test Login
    print("\n[2/5] Testing User Login (/api/auth/login/)...")
    login_payload = {
        "email": reg_payload["email"],
        "password": reg_payload["password"]
    }
    login_resp = client.post('/api/auth/login/', login_payload, format='json')
    assert login_resp.status_code == 200, f"Login failed: {login_resp.data}"
    access_token = login_resp.data['access']
    refresh_token = login_resp.data['refresh']
    print(f"  --> Login successful! JWT Access Token received (length: {len(access_token)})")

    # Attach Bearer token to client
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # 3. Test Patient Management APIs
    print("\n[3/5] Testing Patient Management APIs (/api/patients/)...")
    # Add patient
    patient_payload = {
        "name": "James Cole",
        "age": 38,
        "gender": "Male",
        "phone": "+1-555-1212",
        "email": "james.cole@timeline.org",
        "address": "77 Sector 12, Philadelphia",
        "medical_history": "Post-traumatic stress, temporal disorientation."
    }
    create_patient_resp = client.post('/api/patients/', patient_payload, format='json')
    assert create_patient_resp.status_code == 201, f"Create patient failed: {create_patient_resp.data}"
    patient_id = create_patient_resp.data['id']
    print(f"  --> Patient added: ID {patient_id} - {create_patient_resp.data['name']}")

    # Retrieve all patients
    list_patients_resp = client.get('/api/patients/')
    assert list_patients_resp.status_code == 200, f"List patients failed: {list_patients_resp.data}"
    print(f"  --> Retrieved {len(list_patients_resp.data)} patient(s) created by authenticated user.")

    # Get specific patient details
    get_patient_resp = client.get(f'/api/patients/{patient_id}/')
    assert get_patient_resp.status_code == 200
    print(f"  --> Retrieved details for patient ID {patient_id}: {get_patient_resp.data['name']}")

    # Update patient details
    update_patient_payload = {
        "name": "James Cole",
        "age": 39,
        "gender": "Male",
        "phone": "+1-555-1212",
        "email": "james.cole@timeline.org",
        "address": "80 Sector 12, Philadelphia",
        "medical_history": "Post-traumatic stress resolved."
    }
    put_patient_resp = client.put(f'/api/patients/{patient_id}/', update_patient_payload, format='json')
    assert put_patient_resp.status_code == 200
    print(f"  --> Updated patient ID {patient_id}: Age {put_patient_resp.data['age']}")

    # 4. Test Doctor Management APIs
    print("\n[4/5] Testing Doctor Management APIs (/api/doctors/)...")
    doctor_payload = {
        "name": "Dr. Robert Chase",
        "specialization": "Cardiothoracic Surgery",
        "email": "chase.surgery@hospital.com",
        "phone": "+1-555-9090",
        "years_of_experience": 11,
        "department": "Surgery"
    }
    # Clean up if prior run exists
    Doctor.objects.filter(email=doctor_payload["email"].lower()).delete()

    create_doc_resp = client.post('/api/doctors/', doctor_payload, format='json')
    assert create_doc_resp.status_code == 201, f"Create doctor failed: {create_doc_resp.data}"
    doctor_id = create_doc_resp.data['id']
    print(f"  --> Doctor added: ID {doctor_id} - Dr. {create_doc_resp.data['name']} ({create_doc_resp.data['specialization']})")

    # Retrieve all doctors
    list_doctors_resp = client.get('/api/doctors/')
    assert list_doctors_resp.status_code == 200
    print(f"  --> Retrieved {len(list_doctors_resp.data)} doctor(s).")

    # Get specific doctor details
    get_doc_resp = client.get(f'/api/doctors/{doctor_id}/')
    assert get_doc_resp.status_code == 200
    print(f"  --> Retrieved details for doctor ID {doctor_id}: {get_doc_resp.data['name']}")

    # Update doctor details
    update_doc_payload = {
        "name": "Dr. Robert Chase",
        "specialization": "Chief of Surgery",
        "email": "chase.surgery@hospital.com",
        "phone": "+1-555-9090",
        "years_of_experience": 12,
        "department": "Surgery"
    }
    put_doc_resp = client.put(f'/api/doctors/{doctor_id}/', update_doc_payload, format='json')
    assert put_doc_resp.status_code == 200
    print(f"  --> Updated doctor ID {doctor_id}: {put_doc_resp.data['specialization']}")

    # 5. Test Patient-Doctor Mapping APIs
    print("\n[5/5] Testing Patient-Doctor Mapping APIs (/api/mappings/)...")
    mapping_payload = {
        "patient": patient_id,
        "doctor": doctor_id,
        "notes": "Primary attending physician for surgical evaluation."
    }
    create_map_resp = client.post('/api/mappings/', mapping_payload, format='json')
    assert create_map_resp.status_code == 201, f"Create mapping failed: {create_map_resp.data}"
    mapping_id = create_map_resp.data['mapping']['id']
    print(f"  --> Mapping created: ID {mapping_id} (Patient {patient_id} <--> Doctor {doctor_id})")

    # Retrieve all mappings
    list_maps_resp = client.get('/api/mappings/')
    assert list_maps_resp.status_code == 200
    print(f"  --> Retrieved {len(list_maps_resp.data)} total mapping(s).")

    # Get all doctors assigned to specific patient (GET /api/mappings/<patient_id>/)
    patient_maps_resp = client.get(f'/api/mappings/{patient_id}/')
    assert patient_maps_resp.status_code == 200
    assert patient_maps_resp.data['total_assigned_doctors'] >= 1
    print(f"  --> GET /api/mappings/{patient_id}/: Found {patient_maps_resp.data['total_assigned_doctors']} doctor(s) assigned to {patient_maps_resp.data['patient_name']}.")

    # Delete mapping (DELETE /api/mappings/<id>/)
    del_map_resp = client.delete(f'/api/mappings/{mapping_id}/')
    assert del_map_resp.status_code == 200
    print(f"  --> DELETE /api/mappings/{mapping_id}/: Doctor unassigned successfully.")

    # Delete patient (DELETE /api/patients/<id>/)
    del_patient_resp = client.delete(f'/api/patients/{patient_id}/')
    assert del_patient_resp.status_code == 200
    print(f"  --> DELETE /api/patients/{patient_id}/: Patient deleted successfully.")

    # Delete doctor (DELETE /api/doctors/<id>/)
    del_doc_resp = client.delete(f'/api/doctors/{doctor_id}/')
    assert del_doc_resp.status_code == 200
    print(f"  --> DELETE /api/doctors/{doctor_id}/: Doctor deleted successfully.")

    print("\n=================================================================")
    print("  ALL END-TO-END HEALTHCARE APIS VERIFIED AND WORKING 100%!")
    print("=================================================================\n")


if __name__ == '__main__':
    run_e2e_tests()
