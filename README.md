## Authentication & RBAC System (Django + DRF)

Backend-приложение, реализующее **собственную систему аутентификации и авторизации (RBAC)** без использования готовых решений Django authentication.

Проект реализует:

* регистрацию пользователей
* login/logout через JWT
* обновление профиля
* мягкое удаление пользователя
* систему ролей и разграничения прав доступа (RBAC)
* API для управления ролями и правилами доступа
* mock-ресурсы бизнес-приложения

---

# Технологии

* Python 3.11
* Django
* Django REST Framework
* PostgreSQL
* JWT (PyJWT)
* Docker / Docker Compose
* pytest

---

# Архитектура проекта

```
tzproject/
│
├── authentication/       # аутентификация пользователей
│   ├── utils/
│      └── utils_jwt.py
│   ├── models.py
│   ├── serializers.py
│   ├── authentication.py
│   ├── views.py
│   └── admin_views.py
│
├── business/             # mock бизнес API
│   ├── views.py
│   └── urls.py
│
├── rbac/                 # сервисы RBAC
│   └── services.py
│
├── tests/                # тесты
│   ├── test_auth.py
│   └── test_rbac.py
││
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

# Система аутентификации

Используется **JWT-аутентификация**.

После успешного login пользователю выдаётся токен:

```
Authorization: Bearer <access_token>
```

JWT содержит:

```
user_id
role
jti
iat
exp
```

Для реализации logout используется **blacklist токенов**.

Таблица:

```
BlacklistedToken
```

После logout `jti` токена добавляется в blacklist.

---

# Система авторизации (RBAC)

Реализована **Role Based Access Control** модель.

## Схема базы данных

```
User
 └── role → Role

Role
 └── AccessRoleRule
        └── element → BusinessElement
```

### Таблицы

#### Role

Хранит роли пользователей.

Пример:

```
admin
user
manager
```

---

#### BusinessElement

Описывает объекты системы, к которым осуществляется доступ.

Пример:

```
orders
products
reports
```

---

#### AccessRoleRule

Хранит правила доступа ролей к ресурсам.

```
role_id
element_id

read_permission
read_all_permission

create_permission

update_permission
update_all_permission

delete_permission
delete_all_permission
```

---

## Логика проверки доступа

При запросе:

1. Определяется пользователь по JWT
2. Определяется его роль
3. Получается правило:

```
AccessRoleRule(role, element)
```

4. Проверяется permission в зависимости от HTTP метода

| Метод     | Проверяемое поле                          |
| --------- | ----------------------------------------- |
| GET       | read_permission / read_all_permission     |
| POST      | create_permission                         |
| PUT/PATCH | update_permission / update_all_permission |
| DELETE    | delete_permission / delete_all_permission |

---

# Основные API

## Аутентификация

### Регистрация

```
POST /api/register/
```

Body:

```
{
  "email": "user@test.com",
  "name": "User",
  "password": "password123",
  "password_repeat": "password123"
}
```

Response:

```
{
  "access_token": "...",
  "token_type": "Bearer"
}
```

---

### Login

```
POST /api/login/
```

```
{
  "email": "user@test.com",
  "password": "password123"
}
```

---

### Logout

```
POST /api/logout/
Authorization: Bearer token
```

---

# Профиль пользователя

### Получить профиль

```
GET /api/users/me/
```

---

### Обновить профиль

```
PATCH /api/users/me/
```

---

### Удалить аккаунт (soft delete)

```
DELETE /api/users/me/
```

Пользователь:

```
is_active = False
```

---

# Admin API

Доступно только пользователям с ролью **admin**.

---

### Управление ролями

```
/api/admin/roles/
```

---

### Управление бизнес-ресурсами

```
/api/admin/elements/
```

---

### Управление правилами доступа

```
/api/admin/rules/
```

---

### Управление ролями пользователей

```
/api/admin/users/
```

Администратор может изменить роль пользователя.

---

# Mock бизнес API

Для демонстрации работы RBAC реализованы mock-ресурсы.

---

### Orders

```
GET /api/orders/
POST /api/orders/
```

---

### Products

```
GET /api/products/
```

---

### Reports

```
GET /api/reports/
```

---

# Ошибки доступа

| Код | Причина                     |
| --- | --------------------------- |
| 401 | пользователь не авторизован |
| 403 | нет прав доступа            |

---

# Тесты

Используется **pytest**.

Запуск:

```
pytest
```

Покрытие:

* регистрация
* login
* logout
* RBAC доступ
* RBAC запреты

---

# Запуск проекта

## 1. Клонировать репозиторий

```
git clone https://github.com/afkXesP/access_core.git
cd access_core
```

---

## 2. Создать файл окружения

```
cp .env_example .env
```
---

## 3. Запуск через Docker

```
docker-compose up --build
```

---

# Особенности реализации

* кастомная модель пользователя
* собственная JWT аутентификация
* blacklist токенов
* RBAC система прав
* Admin API для управления доступами
* mock бизнес-ресурсы
* dockerized окружение
* pytest тесты
