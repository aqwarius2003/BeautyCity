from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, unique=True)
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
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    services = models.ManyToManyField(Service, related_name='staff')

    def get_services(self):
        return ", ".join([str(services) for services in self.services.all()])

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Salon(models.Model):
    name = models.CharField(max_length=20, unique=True, default='')
    address = models.CharField(max_length=50, unique=True)
    services = models.ManyToManyField(Service, related_name='salons')
    staff = models.ManyToManyField(Staff, related_name='staff')

    def get_services(self):
        return ", ".join([str(service) for service in self.services.all()])

    def get_staff(self):
        return ', '.join([str(staff) for staff in self.staff.all()])

    def __str__(self):
        return f'{self.name}, {self.address}'


class Appointment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='appointments')
    services = models.ManyToManyField(Service, related_name='appointments')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='appointments')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='appointments', default=1)
    date_time = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    def get_services(self):
        return ", ".join([str(services) for services in self.services.all()])

    def __str__(self):
        return f"Appointment for {self.customer} with {self.staff} on {self.date_time}"






