from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'specialization', 'email', 'phone', 'years_of_experience', 'created_at')
    list_filter = ('specialization', 'created_at')
    search_fields = ('name', 'email', 'phone', 'specialization')
