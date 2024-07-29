# Гайд по работе с БД
Тут можно найти описание моделей, полей этих моделей, а также примеры запросов ОРМ и конечно же хау ту инсталл.

[TOC]

## Install
Нужны вот эти библиотеки:
```
dj-database-url==2.2.0
Django==5.0.7
django-phonenumber-field==8.0.0
phonenumberslite==8.13.40
```
- Скачиваем проект, смотрим чтобы были папки beauty, property файлик бэдэ и manage.py
- Обязательно виртуальное окружение:
```commandline
python3 -m venv .venv
source .venv/bin/activate
```
- Обновляем PIP:
```commandline
pip install --upgrade pip
```
- Ставим библиотеки:

```commandline
pip3 install -r requirements.txt
```

 - Не забываем про первую миграцию:
```commandline
python3 manage.py migrate
```

- Запускаем сервер:
```commandline
python3 manage.py runserver
```

- Идём на локахост/admin

## Описание моделей

### Customer - модель клиента салона красоты:

- `first_name`- имя клиента, передавать в строке
- `last_name` - фамилия клиента, тоже строкой
- `phone` - номер +71234567890, тоже строкой, но если ввести что-то непохожее на реальный номер,  
джанга пошлёт вас за новым номером
- `email` - строкой, но тоже похожей на имейл
- `telegram_id` - целочисленное значение айди телеги клиента, важно для работы БД

 Пример запросов с этой моделью, которые потенциально интересны:
 
```python3
from .models import Customer
from django.shortcuts import get_object_or_404

# даст экземпляр модели клиента если такая есть и выбросит исключение 404 если ееё нет.
get_object_or_404(Customer, telegram_id=909)  

# Тоже самое с try:
try:
    requested_customer = Customer.objects.get(telegram_id=user_tg_id)
except CustomerDoesNptExist:
    raise http404('No Customer matches the given query')

# ну или напиши свой raise какой нужен
```

```python3
# Регистрация нового клиента
Customer.create(
    first_name='Яна', last_name='Несмеяна', phone='+79876543321', 
    email='yanayana@mailbox.wo', telegram_id=99)
```
```python3
from datetime import datetime, timedelta
# открытые записи клиента по айди его телеги
user_appointments = Customer.objects.get(telegram_id=tg_id).appointments.filter(date__gt=datetime.today())
```

### Service
Модель, в которой хранятся услуги (маникюр, педикюр и тд).

- `name` - название услуги, строкой
- `description` - описание услуги, строкой
- `duration` - длительность услуги, timedelta
- `price` - цена, дробное с двумя знаками после запятой

```python3
from .models import Service


all_services = Service.objects.all()    # все услуги
salon_services = salon.get_services()   # все сервисы конкретного салона
staff_services = staff.services()       # сервисы конкретного мастера
```

### Staff
Модель, в которой хранятся профили мастеров, сотрудников салонов.

- `first_name `- имя мастера, передавать в строке
- `last_name` - фамилия мастера, тоже строкой
- `phone` - номер +71234567890, тоже строкой, но если ввести что-то непохожее на реальный номер,  
джанга пошлёт вас за новым номером
- `description` - описание мастера (можно написать сюда разную похвалу)
- `email` - строкой, но тоже похожей на имейл
- `services` - услуги, которые может мастер

```python3
from .models import Staff

# все мастера
Staff.objects.all() 

# мастера в салоне salon
Staff.objects.filter(schedules__salon=salon) 

# мастера которые работают по указанной услуге
staff = Staff.objects.filter(
    services__in=Service.objects.filter(id=requested_service.id)) 

# все даты работы мастера доступные для бронирования 
staff.get_available_dates() 

 # время доступное для записи к мастеру на определенную услугу в определенную дату
staff.get_available_time(requested_service, date)  
```
### Salon

Модель, в которой хранятся профили салонов.

- `name` - название салона, строка
- `address` - адрес салон, строка
- `description` - описание салона, строка

```python3
from .models import Salon


# все салоны
Salon.objects.all() 

# первый салон на улице Ленина
salon = Salon.objects.get(address__contains='Ленина') 

# все услуги выбранного салона на будущие даты (начиная с завтра)
salon.get_services() 

# те же услуги, но в виде словаря с ценами
salon.get_price_list()

# все сотрудники, которые будут работать в салоне начиная с завтра
salon.get_staff() #

# доступные для записи в этот салон даты (надо указать сервис)
salon.get_available_dates(requested_service)

# доступное время (по сервису и дате)
salon.get_available_time(requested_service, date)

# все салоны, в которых работал или будет работать указанный мастер
Salon.objects.filter(schedules__staff=staff)

# салоны, в которых будет оказываться указанный сервис, начиная с завтра
Salon.objects.filter(
    schedules__in=Schedule.objects.filter(
        date__gt=datetime.today(), staff__in=Staff.objects.filter(
            services__in=Service.objects.filter(
                id=requested_service.id)))).distinct()
```

### Schedule

Модель, в которой хранятся графики работы.

- `staff` - FK на модель Staff, мастер, на которого составлен данный график
- `salon` - FK на модель Salon, салон в котором будет работать указанный мастер
- `date` - дата, на которую составлен график, datetime.date
- `start_time` - время начала работы мастера
- `end_time` - время окончания работы мастера

### Appointment

Модель, в которой хранятся все записи клиентов на приём

- `customer` - FK на модель Customer, то есть клиент, который записан на приём
- `service` - FK на модель Service, то есть сервис, на который записан клиент
- `staff` - FK на модель Staff, то есть мастер, к которому записан клиент
- `salon` - FK на модель Salon, то есть салон, в который записан клиент
- `date` - дата, на которую записан клиент, datetime.date(), по-умолчанию - завтра
- `start_time` - время, на которое записан клиент, datetime.time, по умолчанию - 8 утра
- `created_at` - время создания записи, datetime.datetime, по умолчанию - текущее время и дата
- `is_paid` - чекбокс оплачен ли визит клиента, bool, по умолчанию не оплачено

```python3
from .models import Appointment
from datetime import datetime


# все записи
all_aapointments = Appointment.objects.all()

# все записи клиента по его телеграм айди
customer_appointments = Appointment.objects.filter(customer__telegram_id=user_tg_id)

# записи клиента на завтра
customer_future_appointments = customer_appointments.filter(date=(datetime.today() + timedelta(days=1)))

# создание записи с помощью кастомного метода
Appointment.create(user_tg_id, requested_service, staff, salon, date)
```
