Каждый работает в своей папке, затем все это собираем в одно целое.

## Лиза (checkout):
- orders/routers/checkout.py:
  - /orders/checkout (GET/POST)
  - /orders/success/{id}
- orders/service.py:
  - checkout_create_order(...)
- orders/crud/create_orders: 
  - create_order(db, user_id, order_email, total_price) -> Order
  - create_order_items(db, order_id, items) -> list[OrderItem]

## Маша Н. (весь crud и schemas):
- orders/crud/fetch_orders:
  - get_order_for_user(db, order_id, user_id) -> Order
  - get_order_with_items(db, order_id) -> Order (для staff)
  - list_user_orders(db, user_id) -> list[Order]
- orders/schemas.py: схемы деталей и списков

## Соня (роутеры к спискам заказов):
- orders/routers/detail.py: 
  - GET /orders/{order_id} (клиент, с проверкой user_id)
- orders/routers/my.py: 
  - GET /orders/my
- (поиск по email и “все заказы” — уже в features/staff/router.py, но он будет использовать orders.crud)