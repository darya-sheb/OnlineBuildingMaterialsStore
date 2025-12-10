# OnlineBuildingMaterialsStore
Online store for building materials company

Команды запуска для тестирования:
1) создать .env из заготовки:
- cp .env.example .env
2) поднять сервисы:
- docker compose up -d --build
3) создать таблицы (первый запуск или если БД пустая)
- docker compose exec web python -m app.infra.init_db
4) открываем в браузере:
сайт: http://localhost:8000/
health: http://localhost:8000/health
swagger (если нужен): http://localhost:8000/docs
5) остановить:
- docker compose down
6) сбросить БД полностью:
- docker compose down -v

В тестах conftest стирает данные бд каждый раз, поэтому создаете тестовую бд:
1) Создать тестовую БД один раз
- docker compose exec db psql -U app -d postgres -c "CREATE DATABASE app_test;"
  (если скажет “already exists” — это нормально.)

2) Запуск тестов внутри контейнера web (рекомендую, проще всем одинаково)
- docker compose exec -e DATABASE_URL=postgresql+asyncpg://app:app@db:5432/app_test web pytest -q
3) запуск только health
- docker compose exec -e DATABASE_URL=postgresql+asyncpg://app:app@db:5432/app_test web pytest -q tests/test_health.py

---


Фиксируем URLs для параллельной разработки:
## Общие
- GET /health — healthcheck (для тестов/CI)

## Auth - features/auth (dev2)
- GET /auth/register — страница регистрации
- POST /auth/register — регистрация
- GET /auth/login — страница логина
- POST /auth/login — логин
- POST /auth/logout — логаут

## ЛК клиента - features/users (dev2 + dev4)
- GET /profile — профиль
- POST /profile — обновить профиль

## Каталог/товары - features/products (dev5 + dev4)
- GET /products — каталог товаров
- GET /products/{product_id} — карточка товара

## Корзина - features/cart (dev3 + dev4)
- GET /cart — страница корзины
- POST /cart/items/add — добавить товар (product_id, quantity)
- POST /cart/items/{cart_item_id}/set — изменить количество (quantity)
- POST /cart/items/{cart_item_id}/delete — удалить позицию

## Оформление заказа (dev3 + dev4)
- GET /orders/checkout — страница ввода email
- POST /orders/checkout — создать заказ (email -> orders.order_email)
- GET /orders/success/{order_id} — страница успеха с номером

## Заказы (dev5 + dev4)
- GET /orders/my — “Мои заказы” (по текущему пользователю)
- GET /orders/{order_id} — детали заказа (по id) - для работника

## Staff - features/staff (dev5 + dev4)
- GET /staff — панель работника
- GET /staff/products — товары (таблица)
- GET + POST /staff/products/new — добавить товар (с фото)
- GET + POST /staff/products/{product_id}/edit — редактировать
- POST /staff/products/{product_id}/stock — изменить остаток
- GET /staff/orders — все заказы (берется функция из orders, см. README.md в features/orders)
- GET /staff/orders/{order_id} — детали
- GET /staff/orders/search?email=... — поиск заказов по email