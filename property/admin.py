from django.contrib import admin
from .models import Customer, Service, Staff, Appointment, Salon


@admin.register(Customer)
class FlatAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    list_display = ('first_name', 'last_name', 'phone', 'email', 'telegram_id')
    list_filter = ('first_name', 'last_name', 'phone', 'email')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    search_fields = ('name', 'price')
    list_display = ('name', 'description', 'duration', 'price')
    list_filter = ('name', 'price')


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name')
    list_display = ('first_name', 'last_name', 'phone', 'email', 'get_services')
    list_filter = ('services',)
    raw_id_fields = ('services',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    search_fields = ('customer',)
    list_display = ('customer', 'get_services', 'staff', 'date_time', 'salon', 'created_at')
    list_filter = ('services', 'staff', 'salon')
    readonly_fields = ('created_at',)
    raw_id_fields = ('customer', 'services', 'staff', 'salon')


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    search_fields = ('address',)
    list_display = ('name', 'address', 'get_services', 'get_staff')
    list_filter = ('services',)
    raw_id_fields = ('services',)
