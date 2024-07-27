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
        return f'{self.first_name }: {", ".join([service.name for service in self.services.all()])}'


class Salon(models.Model):
    name = models.CharField(max_length=20, unique=True, default='')
    address = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=256, default='')

    def get_services(self):
        services = Service.objects.filter(staff__schedules__salon=self).distinct()
        return services

    def get_staff(self):
        staff = Staff.objects.filter(schedules__salon=self).distinct()
        return staff

    # from property.models import Customer, Service, Staff, Salon, Schedule, Appointment, TimeSlot
    # salon = Salon.objects.get(address__contains='Ленина')

    def get_price_list(self):
        price_list = self.get_services().values('name', 'price')
        return price_list

    def get_schedules(self):
        return ''.join([f'{schedule.staff.first_name} {schedule.staff.last_name} {schedule.date} / ' for schedule in self.schedules.all()])

    def get_available_dates(self, requested_service):
        available_dates = self.schedules.filter(
            staff__services__in=Service.objects.filter(
                name__contains=requested_service)).distinct().values_list('date', flat=True)
        return available_dates

    def get_available_time(self, requested_service, date):
        schedule = self.schedules.filter(
            date=date, staff__services__in=Service.objects.filter(name__contains=requested_service))

        return

    def __str__(self):
        return f'{self.name}, {self.address}'


class Schedule(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='schedules')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    start_time = models.TimeField(default='08:00:00')
    end_time = models.TimeField(default='18:00:00')

    def get_services(self):
        return [service.name for service in self.staff.services.all()]

    def get_appointments(self):
        return Appointment.objects.get(date=self.date).get_total_duration()

    def __str__(self):
        return f"Schedule for {self.staff} at {self.salon} on {self.date} from {self.start_time} to {self.end_time}"


class Appointment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='appointments')
    services = models.ManyToManyField(Service, related_name='appointments')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='appointments')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField(default=datetime.today().strftime('%Y-%m-%d'))
    start_time = models.TimeField(default='08:00:00')
    created_at = models.DateTimeField(default=timezone.now)

    def get_services(self):
        return ", ".join([service.name for service in self.services.all()])

    def get_total_duration(self):
        return self.services.aggregate(total_duration=models.Sum('duration'))['total_duration']

    def __str__(self):
        return f"Appointment for {self.customer} with {self.staff} on {self.date}, {self.start_time}"


class TimeSlot(models.Model):
    duration = models.DurationField()
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='timeslots')
    date = models.DateField()
    start_time = models.TimeField(default='08:00:00')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, related_name='timeslots')

    def __str__(self):
        return f'Timeslot {self.staff} {self.duration} {self.date}'
