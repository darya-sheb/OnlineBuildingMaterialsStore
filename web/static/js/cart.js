document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', async function (e) {
            e.preventDefault();

            const productId = this.getAttribute('data-product-id');
            const input = document.querySelector(`input[data-product-id="${productId}"]`);
            const quantity = input ? parseInt(input.value) || 1 : 1;

            try {
                const response = await fetch('/cart/items/', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        product_id: parseInt(productId),
                        quantity: quantity
                    })
                });

                if (response.ok) {
                    alert('Товар добавлен в корзину!');
                } else {
                    let errorMsg = 'Не удалось добавить товар';
                    try {
                        const error = await response.json();
                        errorMsg = error.detail || errorMsg;
                    } catch (e) {
                        if (response.status === 404) {
                            errorMsg = 'Товар не найден в базе. Свяжитесь с администратором.';
                        } else if (response.status === 500) {
                            errorMsg = 'Ошибка сервера. Попробуйте позже.';
                        }
                    }
                    alert('Ошибка: ' + errorMsg);
                }
            } catch (err) {
                alert('Ошибка подключения');
                console.error(err);
            }
        });
    });

    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', async function () {
            if (!confirm('Удалить товар из корзины?')) return;

            const cartItemId = this.getAttribute('data-cart-item-id');

            try {
                const response = await fetch(`/cart/items/${cartItemId}`, {
                    method: 'DELETE',
                    credentials: 'include'
                });

                if (response.ok) {
                    location.reload();
                } else {
                    alert('Не удалось удалить товар');
                }
            } catch (err) {
                alert('Ошибка подключения');
            }
        });
    });

    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', async function () {
            const cartItemId = this.getAttribute('data-cart-item-id');
            const newQuantity = parseInt(this.value);
            if (isNaN(newQuantity) || newQuantity < 1) return;

            try {
                const response = await fetch(`/cart/items/${cartItemId}`, {
                    method: 'PUT',
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ quantity: newQuantity })
                });

                if (response.ok) {
                    location.reload();
                }
            } catch (err) {
                console.error(err);
            }
        });
    });
});
