from django.contrib import admin
from .models import Customer, Service, Staff, Appointment, Salon, StaffSchedule


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    list_display = ('first_name', 'last_name', 'phone', 'email', 'telegram_id')
    list_filter = ('first_name', 'last_name', 'phone', 'email')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    search_fields = ('name', 'price')
    list_display = ('name', 'description', 'duration', 'price')
    list_filter = ('name', 'price')


class PropertyAppointmentStaff(admin.TabularInline):
    model = Appointment
    raw_id_fields = ('customer',)
    extra = 0


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name')
    list_display = ('first_name', 'last_name', 'phone', 'email', 'get_services')
    list_filter = ('services',)
    raw_id_fields = ()
    inlines = [PropertyAppointmentStaff, ]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    search_fields = ('customer',)
    list_display = ('customer', 'get_services', 'staff', 'date_time', 'get_total_duration', 'salon', 'created_at')
    list_filter = ('services', 'staff', 'salon')
    readonly_fields = ('created_at',)
    raw_id_fields = ('customer',)


class PropertyStaffScheduleSalon(admin.TabularInline):
    model = StaffSchedule
    raw_id_fields = ()
    extra = 0


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    search_fields = ('address',)
    list_display = ('name', 'address', 'get_schedules')
    list_filter = ()
    raw_id_fields = ()
    inlines = [PropertyAppointmentStaff, PropertyStaffScheduleSalon]


@admin.register(StaffSchedule)
class StaffScheduleAdmin(admin.ModelAdmin):
    list_display = ('staff', 'salon', 'get_services', 'date', 'start_time', 'end_time', )
    raw_id_fields = ()
