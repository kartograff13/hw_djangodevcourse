# hw_djangodevcourse — LMS-платформа для онлайн-обучения

Проект представляет собой backend-часть платформы для онлайн-обучения с возможностью создания курсов, уроков, управления подписками, оплатой через Stripe и разграничением прав (пользователи, модераторы, администраторы).

## 🚀 Основной функционал

- **Пользователи**: регистрация, JWT-аутентификация, просмотр/редактирование профиля, публичные профили.
- **Курсы и уроки**: CRUD, владельцы, модераторы (просмотр/редактирование без создания/удаления), пагинация, фильтрация.
- **Подписки**: пользователи могут подписываться на обновления курса (один раз).
- **Платежи**: интеграция с Stripe (создание продукта, цены, сессии, проверка статуса).
- **Документация API**: автоматическая (drf-spectacular) — Swagger UI и ReDoc.

## 🛠 Технологии

- Python 3.14
- Django 6.0.3
- Django REST Framework 3.17
- PostgreSQL
- JWT (djangorestframework-simplejwt)
- Stripe API
- drf-spectacular (OpenAPI)
- django-filter
- django-phonenumber-field
- Pillow (для изображений)
- Black, isort, flake8 (линтеры)
- Docker / Docker Compose

## 🐳 Запуск через Docker (рекомендованный способ)
### 1. Клонируйте репозиторий

```
git clone <url вашего репозитория>
cd hw_djangodevcourse
```

### 2. Создайте файл .env (см. .env.sample ниже).
##### Убедитесь, что DB_HOST=db (имя сервиса в compose).

### 3. Запустите контейнеры
```bash
docker-compose up --build
```

### 4. Выполните миграции и создайте суперпользователя (в другом терминале)
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 5. Проект доступен:
- **Django API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/api/schema/swagger/
- **pgAdmin**: http://localhost:5050 (логин: admin@admin.com, пароль: admin)

#### Остановка: ```docker-compose down```

## 🔧 Ручная установка (без Docker)

### 1. Клонирование репозитория
```
git clone <url вашего репозитория>
cd hw_djangodevcourse
```

### 2. Создание и активация виртуального окружения
```
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows
```

### 3. Установка зависимостей
```commandline
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
Создайте файл .env в корне проекта со следующим содержимым из примера ***.env.sample***.

### 5. Применение миграций
```
python manage.py makemigrations
python manage.py migrate
```

### 6. Создание суперпользователя
```commandline
python manage.py createsuperuser
```

### 7. Заполнение тестовыми данными (опционально)
```
python manage.py create_test_data   # создаёт пользователей, курсы, уроки, платежи
python manage.py create_moderator_group
```

### 8. Запуск сервера разработки
```commandline
python manage.py runserver
```

## 📚 Документация API
### После запуска сервера документация доступна по адресам:

Swagger UI: http://127.0.0.1:8000/api/schema/swagger/

ReDoc: http://127.0.0.1:8000/api/schema/redoc/

OpenAPI JSON: http://127.0.0.1:8000/api/schema/

## 🧪 Тестирование
### Запуск всех тестов:
```commandline
python manage.py test
```

### Покрытие кода (coverage):
```
coverage run manage.py test
coverage report
```

## 🔐 Основные эндпоинты
### Метод	URL	Описание
- **POST**	```/api/register/```	*Регистрация пользователя*
- **POST**	```/api/token/```	*Получение JWT-токена*
- **POST**	```/api/token/refresh/```	*Обновление access-токена*
- **GET**	```/api/profile/```	*Свой профиль (полный)*
- **GET**	```/api/profiles/<id>/```	*Публичный профиль*
- **GET**	```/api/courses/```	*Список курсов (пагинация)*
- **POST**	```/api/courses/```	*Создание курса*
- **GET**	```/api/lessons/```	*Список уроков*
- **POST**	```/api/subscribe/```	*Подписка/отписка от курса*
- **POST**	```/api/payments/create/```	*Создание платежа через Stripe*
- **GET**	```/api/payments/status/<id>/```	*Проверка статуса платежа*
#### Полный список и параметры — в документации Swagger.

## 👥 Роли и права доступа
- **Обычный пользователь**: создаёт, редактирует, удаляет свои курсы/уроки; просматривает публичные профили; подписывается на курсы; оплачивает.
- **Модератор (группа Модераторы)**: может просматривать и редактировать любые курсы/уроки, НО не может их создавать и удалять.
- **Администратор**: полный CRUD пользователей, платежей и всего контента через админ-панель.

## 💳 Оплата через Stripe
- При POST `````/api/payments/create/````` с ```course_id``` создаётся продукт, цена и сессия в Stripe.
- В ответе возвращается ```payment_url``` — ссылка на checkout Stripe.
- После оплаты пользователь перенаправляется на ```/stripe/success/``` или ```/stripe/cancel/```.
- Статус платежа можно проверить через ```/api/payments/status/<payment_id>/```.

### Тестовые карты Stripe:

- Успешная оплата: ```4242 4242 4242 4242```
- Требуется аутентификация: ```4000 0025 0000 3155```
- Отказ: ```4000 0000 0000 0002```

## 🧰 Полезные команды
```
# Создание группы модераторов
python manage.py create_moderator_group

# Заполнение тестовыми данными
python manage.py create_test_data

# Форматирование кода (black)
black .

# Сортировка импортов (isort)
isort .

# Проверка flake8
flake8

# Docker: остановка контейнеров
docker-compose down

# Docker: просмотр логов
docker-compose logs -f web
```

## 📄 Лицензия
****Учебный проект, создан в рамках курса по разработке на Django.****
