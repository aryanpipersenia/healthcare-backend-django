# Healthcare Backend System 🏥

A secure, scalable RESTful API backend for a Healthcare Application built with **Django**, **Django REST Framework (DRF)**, **PostgreSQL**, and **JWT Authentication** (`djangorestframework-simplejwt`).

---

## 🌟 Key Features

- **JWT Authentication**: User registration and login with encrypted passwords and stateless JWT access/refresh tokens.
- **Patient Management**: Complete CRUD operations for patient records with strict creator-ownership isolation (users can only manage patients they created).
- **Doctor Management**: Complete CRUD operations for doctor profiles, specialties, and experience records.
- **Patient-Doctor Mapping**: Assign doctors to patients, prevent duplicate assignments, query all doctors for a specific patient, and remove mappings.
- **PostgreSQL Database**: Configured via `.env` environment variables using Django ORM.
- **Robust Error Handling**: Standardized JSON error responses and field-level validation across all endpoints.
- **Interactive Postman Collection**: Ready-to-use Postman collection and environment files included.

---

## 🏗️ Project Architecture

```
AssignmentWB/
│
├── .env                                # Environment configurations (DB, secrets, JWT)
├── .env.example                        # Template for environment configurations
├── manage.py                           # Django CLI entrypoint
├── requirements.txt                    # Project dependencies
├── Healthcare_Backend_Postman_Collection.json # Postman collection for all APIs
├── Healthcare_Postman_Environment.json  # Postman environment variables
├── test_api_client.py                  # End-to-end integration test runner
│
├── healthcare_project/                 # Project core configuration
│   ├── __init__.py
│   ├── settings.py                     # PostgreSQL, JWT, CORS, DRF settings
│   ├── urls.py                         # Root URL routing & API discovery endpoint
│   ├── exceptions.py                   # Custom error handler for uniform JSON responses
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/                           # Custom User model & JWT authentication
│   ├── models.py                       # User model (email-based login)
│   ├── serializers.py                  # Register & Login serializers
│   ├── views.py                        # RegisterView, LoginView, UserProfileView
│   ├── urls.py                         # /api/auth/*
│   ├── tests.py                        # Auth test suite
│   └── admin.py
│
├── patients/                           # Patient records management
│   ├── models.py                       # Patient model linked to creator User
│   ├── serializers.py                  # Patient serializer with validation
│   ├── views.py                        # PatientViewSet (CRUD)
│   ├── urls.py                         # /api/patients/*
│   ├── tests.py                        # Patient test suite
│   └── admin.py
│
├── doctors/                            # Doctor directory management
│   ├── models.py                       # Doctor model with experience & specialization
│   ├── serializers.py                  # Doctor serializer with validation
│   ├── views.py                        # DoctorViewSet (CRUD)
│   ├── urls.py                         # /api/doctors/*
│   ├── tests.py                        # Doctor test suite
│   └── admin.py
│
└── mappings/                           # Patient-to-Doctor assignment
    ├── models.py                       # PatientDoctorMapping with UniqueConstraint
    ├── serializers.py                  # Mapping serializer & doctor listing serializer
    ├── views.py                        # Assign, list, patient-specific lookup, unassign
    ├── urls.py                         # /api/mappings/*
    ├── tests.py                        # Mapping test suite
    └── admin.py
```

---

## 🛠️ Tech Stack & Dependencies

- **Language**: Python 3.12+
- **Backend Framework**: Django 6.1+
- **API Framework**: Django REST Framework (DRF) 3.18+
- **Authentication**: `djangorestframework-simplejwt` 5.5+
- **Database**: PostgreSQL 17 (via `psycopg2-binary`)
- **Environment Management**: `python-dotenv`
- **CORS Support**: `django-cors-headers`

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ installed
- PostgreSQL installed and running on `localhost:5432`

### 2. Environment Setup
```bash
# Clone/navigate to project directory
cd AssignmentWB

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Configuration (`.env`)
Create a `.env` file in the root directory (or use the provided `.env`):
```env
SECRET_KEY=django-insecure-healthcare-backend-super-secret-key-2026-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# PostgreSQL Configuration
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=Aryan
DB_HOST=localhost
DB_PORT=5432

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

### 4. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin Superuser (Optional)
A pre-configured admin account is already available:
- **Email**: `admin@healthcare.com`
- **Password**: `Admin@123456`

To create your own custom superuser:
```bash
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver 8000
```
The server will start at: `http://127.0.0.1:8000/`

---

## 🧪 Running Automated Tests

### Full Django Test Suite (26 automated test cases against PostgreSQL):
```bash
python manage.py test
```

### End-to-End API Integration Verification:
```bash
python test_api_client.py
```

---

## 📑 API Documentation & Reference

### 🔐 1. Authentication APIs

#### 1.1 Register User
- **Method**: `POST`
- **URL**: `/api/auth/register/`
- **Access**: Public
- **Request Body**:
```json
{
  "name": "Dr. Gregory House",
  "email": "house.md@hospital.com",
  "password": "Diagnostician2026!"
}
```
- **Response (`201 Created`)**:
```json
{
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "name": "Dr. Gregory House",
    "email": "house.md@hospital.com",
    "date_joined": "2026-10-28T17:00:00Z"
  },
  "tokens": {
    "refresh": "eyJhbGciOi...",
    "access": "eyJhbGciOi..."
  }
}
```

#### 1.2 User Login (Obtain JWT)
- **Method**: `POST`
- **URL**: `/api/auth/login/`
- **Access**: Public
- **Request Body**:
```json
{
  "email": "house.md@hospital.com",
  "password": "Diagnostician2026!"
}
```
- **Response (`200 OK`)**:
```json
{
  "message": "Login successful.",
  "user": {
    "id": 1,
    "name": "Dr. Gregory House",
    "email": "house.md@hospital.com"
  },
  "access": "eyJhbGciOi...",
  "refresh": "eyJhbGciOi..."
}
```

#### 1.3 Refresh Token
- **Method**: `POST`
- **URL**: `/api/auth/token/refresh/`
- **Request Body**: `{"refresh": "<refresh_token>"}`

---

### 🏥 2. Patient Management APIs
*Header required for all endpoints: `Authorization: Bearer <access_token>`*

#### 2.1 Add a New Patient
- **Method**: `POST`
- **URL**: `/api/patients/`
- **Request Body**:
```json
{
  "name": "John Doe",
  "age": 45,
  "gender": "Male",
  "phone": "+1-555-0199",
  "email": "johndoe@example.com",
  "address": "42 Medical Center Blvd",
  "medical_history": "Hypertension, pollen allergy"
}
```
- **Response (`201 Created`)**:
```json
{
  "id": 1,
  "name": "John Doe",
  "age": 45,
  "gender": "Male",
  "phone": "+1-555-0199",
  "email": "johndoe@example.com",
  "address": "42 Medical Center Blvd",
  "medical_history": "Hypertension, pollen allergy",
  "created_by": 1,
  "created_by_name": "Dr. Gregory House",
  "created_at": "2026-10-28T17:05:00Z"
}
```

#### 2.2 Retrieve All Patients Created by Authenticated User
- **Method**: `GET`
- **URL**: `/api/patients/`
- **Response (`200 OK`)**: Array of patient objects created by the logged-in user.

#### 2.3 Get Specific Patient Details
- **Method**: `GET`
- **URL**: `/api/patients/<id>/`
- **Response (`200 OK`)**: Patient object details.

#### 2.4 Update Patient Details
- **Method**: `PUT` (or `PATCH`)
- **URL**: `/api/patients/<id>/`
- **Request Body**: Same format as create.

#### 2.5 Delete Patient Record
- **Method**: `DELETE`
- **URL**: `/api/patients/<id>/`
- **Response (`200 OK`)**:
```json
{
  "message": "Patient 'John Doe' (ID: 1) deleted successfully."
}
```

---

### 👨‍⚕️ 3. Doctor Management APIs
*Header required: `Authorization: Bearer <access_token>`*

#### 3.1 Add a New Doctor
- **Method**: `POST`
- **URL**: `/api/doctors/`
- **Request Body**:
```json
{
  "name": "Dr. Allison Cameron",
  "specialization": "Immunology",
  "email": "cameron.allison@hospital.com",
  "phone": "+1-555-0844",
  "years_of_experience": 12,
  "department": "Immunology & Allergy"
}
```
- **Response (`201 Created`)**: Doctor record created.

#### 3.2 Retrieve All Doctors
- **Method**: `GET`
- **URL**: `/api/doctors/`
- **Response (`200 OK`)**: List of all registered doctors.

#### 3.3 Get Specific Doctor Details
- **Method**: `GET`
- **URL**: `/api/doctors/<id>/`
- **Response (`200 OK`)**: Specific doctor details.

#### 3.4 Update Doctor Details
- **Method**: `PUT` (or `PATCH`)
- **URL**: `/api/doctors/<id>/`
- **Request Body**: Updated fields.

#### 3.5 Delete Doctor Record
- **Method**: `DELETE`
- **URL**: `/api/doctors/<id>/`
- **Response (`200 OK`)**:
```json
{
  "message": "Doctor 'Dr. Allison Cameron' (ID: 1) deleted successfully."
}
```

---

### 🔗 4. Patient-Doctor Mapping APIs
*Header required: `Authorization: Bearer <access_token>`*

#### 4.1 Assign Doctor to Patient
- **Method**: `POST`
- **URL**: `/api/mappings/`
- **Request Body**:
```json
{
  "patient": 1,
  "doctor": 1,
  "notes": "Primary consulting physician assignment."
}
```
- **Response (`201 Created`)**:
```json
{
  "message": "Doctor assigned to patient successfully.",
  "mapping": {
    "id": 1,
    "patient": 1,
    "patient_name": "John Doe",
    "doctor": 1,
    "doctor_name": "Dr. Allison Cameron",
    "doctor_specialization": "Immunology",
    "assigned_at": "2026-10-28T17:10:00Z",
    "notes": "Primary consulting physician assignment."
  }
}
```

#### 4.2 Retrieve All Patient-Doctor Mappings
- **Method**: `GET`
- **URL**: `/api/mappings/`
- **Response (`200 OK`)**: Array of all active patient-doctor mapping records.

#### 4.3 Get All Doctors Assigned to a Specific Patient
- **Method**: `GET`
- **URL**: `/api/mappings/<patient_id>/` *(also accessible via `/api/mappings/patient/<patient_id>/`)*
- **Response (`200 OK`)**:
```json
{
  "patient_id": 1,
  "patient_name": "John Doe",
  "total_assigned_doctors": 1,
  "doctors": [
    {
      "mapping_id": 1,
      "doctor_id": 1,
      "doctor_name": "Dr. Allison Cameron",
      "specialization": "Immunology",
      "email": "cameron.allison@hospital.com",
      "phone": "+1-555-0844",
      "years_of_experience": 12,
      "department": "Immunology & Allergy",
      "assigned_at": "2026-10-28T17:10:00Z",
      "notes": "Primary consulting physician assignment."
    }
  ]
}
```

#### 4.4 Remove a Doctor from a Patient
- **Method**: `DELETE`
- **URL**: `/api/mappings/<id>/`
- **Response (`200 OK`)**:
```json
{
  "message": "Successfully unassigned Dr. Allison Cameron from Patient John Doe.",
  "deleted_mapping_id": 1
}
```

---

## 📮 Testing with Postman

1. Open **Postman**.
2. Click **Import** (top left).
3. Select `Healthcare_Backend_Postman_Collection.json` and `Healthcare_Postman_Environment.json`.
4. In the top-right environment selector, choose **"Healthcare Backend Local"**.
5. Run the requests in order:
   - **Authentication -> Register User** (automatically sets `token` and `refresh_token` variables).
   - **Patient Management -> Add New Patient** (automatically sets `patient_id`).
   - **Doctor Management -> Add New Doctor** (automatically sets `doctor_id`).
   - **Patient-Doctor Mapping -> Assign Doctor to Patient** (automatically sets `mapping_id`).
   - Test all retrieval, update, and deletion endpoints!
