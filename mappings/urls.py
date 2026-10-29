from django.urls import path
from .views import (
    MappingDetailOrPatientDoctorsView,
    MappingListCreateView,
    PatientDoctorsListView,
)

urlpatterns = [
    path('', MappingListCreateView.as_view(), name='mapping-list-create'),
    path('patient/<int:patient_id>/', PatientDoctorsListView.as_view(), name='patient-doctors-dedicated'),
    path('<int:identifier>/', MappingDetailOrPatientDoctorsView.as_view(), name='mapping-detail-or-patient'),
]
