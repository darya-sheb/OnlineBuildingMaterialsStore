
## Лиза (checkout):
- orders/routers/checkout.py:
  - /orders/checkout (GET/POST)
  - /orders/success/{id}
- orders/service.py:
  - checkout_create_order(...)
- orders/crud/create_orders: 
  - create_order(db, user_id, order_email, total_price) -> Order
  - create_order_items(db, order_id, items) -> list[OrderItem]