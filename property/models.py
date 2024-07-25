from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime, timedelta


class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = PhoneNumberField(unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    telegram_id = models.IntegerField(unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.DurationField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Staff(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = PhoneNumberField(unique=True)
    description = models.TextField(max_length=256, default='')
    email = models.EmailField(unique=True)
    services = models.ManyToManyField(Service, related_name='staff')

    def get_services(self):
        return ", ".join([service.name for service in self.services.all()])

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Salon(models.Model):
    name = models.CharField(max_length=20, unique=True, default='')
    address = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=256, default='')

    def get_schedules(self):
        return ''.join([f'{schedule.staff.first_name} {schedule.staff.last_name} {schedule.date} / ' for schedule in self.schedules.all()])

    def __str__(self):
        return f'{self.name}, {self.address}'


class StaffSchedule(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='schedules')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def get_services(self):
        return ", ".join([service.name for service in self.staff.services.all()])

    def __str__(self):
        return f"Schedule for {self.staff} at {self.salon} on {self.date} from {self.start_time} to {self.end_time}"


class Appointment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='appointments')
    services = models.ManyToManyField(Service, related_name='appointments')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='appointments')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='appointments')
    date_time = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    def get_services(self):
        return ", ".join([service.name for service in self.services.all()])

    def get_total_duration(self):
        return self.services.aggregate(total_duration=models.Sum('duration'))['total_duration']

    def __str__(self):
        return f"Appointment for {self.customer} with {self.staff} on {self.date_time}"