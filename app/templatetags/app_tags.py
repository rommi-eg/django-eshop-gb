from django import template
from app.models import FavoriteProduct, OrderProduct, Order, Customer


register = template.Library()


@register.simple_tag()
def get_favorite_products(user):
    """
    Получает список избранных продуктов пользователя.
    """
    favorites_products = FavoriteProduct.objects.filter(
        user=user,
    )
    products = [item.product for item in favorites_products]
    return products


@register.simple_tag()
def get_cart_count(user):
    try:
        customer = Customer.objects.get(
            user=user
        )
        return Order.objects.get(pk=customer.pk).get_cart_total_quantity
    except:
        return '0'
