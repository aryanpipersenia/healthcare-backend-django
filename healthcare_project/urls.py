"""
URL configuration for healthcare_project project.
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Overview of all available Healthcare Management APIs.
    """
    return Response({
        "project": "Healthcare Backend System",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "authentication": {
                "register": "/api/auth/register/",
                "login": "/api/auth/login/",
                "token_refresh": "/api/auth/token/refresh/",
                "profile": "/api/auth/profile/",
            },
            "patients": {
                "list_and_create": "/api/patients/",
                "detail_update_delete": "/api/patients/<id>/",
            },
            "doctors": {
                "list_and_create": "/api/doctors/",
                "detail_update_delete": "/api/doctors/<id>/",
            },
            "patient_doctor_mappings": {
                "assign_and_list": "/api/mappings/",
                "patient_doctors_and_delete_mapping": "/api/mappings/<id_or_patient_id>/",
                "patient_doctors_dedicated": "/api/mappings/patient/<patient_id>/",
            },
            "admin": "/admin/",
        }
    })


urlpatterns = [
    path('', api_root, name='api-root-base'),
    path('api/', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/patients/', include('patients.urls')),
    path('api/doctors/', include('doctors.urls')),
    path('api/mappings/', include('mappings.urls')),
]
