# Гайд по работе с БД
Тут можно найти описание моделей, полей этих моделей, а также примеры запросов ОРМ и конечно же хау ту инсталл.

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
pip3 install Django==5.0.7, dj-database-url==2.2.0, django-phonenumber-field==8.0.0, phonenumberslite==8.13.40
```
ну или просто:
```commandline
pip3 install -r requirements.txt
```
- Запускаем сервер:
```commandline
python3 manage.py runserver
```
 - Понимаем что забыли инициализирующую миграцию:
```commandline
python3 manage.py migrate
```
- Снова поднимаем сервер с колен и идём на локахост/admin

## Описание моделей

### Customer - модель клиента салона красоты:

- `first_name `- имя клиента, передавать в строке
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
Customer.objects.create(
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


Staff.objects.all() # все мастера

Staff.objects.filter(schedules__salon=salon) # мастера в салоне salon

# мастера которые работают по указанной услуге
staff = Staff.objects.filter(
    services__in=Service.objects.filter(id=requested_service.id)) 
```
