from typing import Dict, List, Optional

carts: Dict[str, List[dict]] = {}

def get_cart(ses_id: str) -> List[dict]:
    if ses_id not in carts:
        carts[ses_id] = []
    return carts[ses_id]

def add_to_cart(ses_id: str, product_id: int, quantity: int = 1) -> dict:
    cart = get_cart(ses_id)
    for i in cart:
        if i["product_id"] == product_id:
            i["quantity"] += quantity
            return i
    neww = {"cart_item_id": len(cart) + 1, "product_id": product_id, "quantity": quantity }
    cart.append(neww)
    return neww


def get_cart_items(ses_id: str) -> List[dict]:
    return get_cart(ses_id)

def get_cart_item(ses_id: str, cart_item_id: int) -> Optional[dict]:
    for i in get_cart_items(ses_id):
        if i["cart_item_id"] == cart_item_id:
            return i
    return None

def update_cart_item(ses_id: str, cart_item_id: int, quantity: int) -> Optional[dict]:
    if i := get_cart_item(ses_id, cart_item_id):
        i["quantity"] = quantity
        return i
    return None

def remove_from_cart(ses_id: str, cart_item_id: int) -> bool:
    cart = get_cart(ses_id)
    for i, item in enumerate(cart):
        if item["cart_item_id"] == cart_item_id:
            cart.pop(i)
            return True
    return False

def clear_cart(session_id: str) -> None:
    if session_id in carts:
        carts[session_id] = []