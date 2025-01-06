from .models import Product, Order, OrderProduct, Customer


class CartForAuthenticatedUser:
    """
    Класс для управления корзиной покупок для аутентифицированных пользователей.
    """

    def __init__(self, request, product_id=None, action=None):
        """
        Инициализация корзины для аутентифицированного пользователя.
        """
        self.user = request.user
        if product_id and action:
            self.add_or_delete(
                product_id=product_id,
                action=action
            )

    def get_cart_info(self):
        """
        Получение информации о корзине пользователя.
        """
        customer, created = Customer.objects.get_or_create(
            user=self.user
        )
        order, created = Order.objects.get_or_create(
            customer=customer
        )
        order_products = order.ordered.all()
        cart_total_quantity = order.get_cart_total_quantity
        cart_total_price = order.get_cart_total_price

        return {
            'order': order,
            'order_products': order_products,
            'cart_total_quantity': cart_total_quantity,
            'cart_total_price': cart_total_price,
        }

    def add_or_delete(self, product_id, action):
        """
        Добавление, удаление или полное удаление продукта из корзины.
        """
        order = self.get_cart_info().get('order')
        product = Product.objects.get(pk=product_id)
        order_product, created = OrderProduct.objects.get_or_create(
            order=order,
            product=product,
        )
        if action == 'add' and product.product_quantity > 0:
            order_product.quantity += 1
            product.product_quantity -= 1
        elif action == 'delete':
            order_product.quantity -= 1
            product.product_quantity += 1
        elif action == 'remove':
            product.product_quantity += order_product.quantity
            order_product.quantity -= order_product.quantity

        product.save()
        order_product.save()

        if order_product.quantity < 1:
            order_product.delete()

    def clear(self):
        """ Удаление всех товаров из корзины """
        order = self.get_cart_info()['order']
        order_products = order.ordered.all()
        for product in order_products:
            product.delete()
        order.save()


def get_cart_data(request):
    """
    Получение данных корзины для текущего пользователя.
    """
    cart = CartForAuthenticatedUser(request=request)
    cart_info = cart.get_cart_info()

    return {
        'order': cart_info['order'],
        'order_products': cart_info['order_products'],
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'cart_total_price': cart_info['cart_total_price'],
    }
