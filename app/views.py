import stripe

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.db.models import F
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from .forms import LoginForm, RegistrationForm, CustomerForm, ShippingForm, Customer
from .models import Category, Product, FavoriteProduct
from .utils import CartForAuthenticatedUser, get_cart_data
from config import settings


class MainPage(ListView):
    """
    Представление для главной страницы с использованием ListView.
    Отображает список основных категорий (без родителя).
    """
    model = Product
    context_object_name = 'categories'
    extra_context = {
        'title': 'Главная страница'
    }
    template_name = 'index.html'

    def get_queryset(self):
        """
        Переопределяем метод для формирования запроса.
        Возвращает только категории верхнего уровня (без родителя).
        """
        return Category.objects.filter(parent=None)

    def get_context_data(self, **kwargs):
        """
        Переопределение метода для добавления дополнительных данных в контекст шаблона.
        """
        context = super().get_context_data()
        context['top'] = Product.objects.order_by('-product_watched')[:3]

        return context


class SubCategories(ListView):
    """
    Представление для отображения товаров в конкретной категории и её подкатегориях.
    """
    model = Product
    context_object_name = 'products'
    template_name = 'category.html'

    paginate_by = 9

    def get_queryset(self):
        """
        Переопределение метода для получения набора данных (QuerySet).
        Возвращает список товаров в текущей категории или её подкатегориях.
        """
        type_field = self.request.GET.get('type')

        if type_field:
            products = Product.objects.filter(
                product_category__slug=type_field
            )
            return products

        parent_category = Category.objects.get(
            slug=self.kwargs['slug']
        )

        subcategories = parent_category.subcategories.all()
        products = Product.objects.filter(
            product_category__in=subcategories
        )

        return products

    def get_context_data(self, **kwargs):
        """
        Переопределение метода для добавления дополнительных данных в контекст шаблона.
        """
        context = super().get_context_data(**kwargs)
        parent_category = Category.objects.get(
            slug=self.kwargs['slug']
        )
        context['category'] = parent_category
        context['title'] = parent_category.category_name
        context['filters'] = Category.objects.filter(
            parent=parent_category
        )

        return context


class ProductPage(DetailView):
    """ 
    Представление для отображения детальной информации о конкретном продукте.
    """
    model = Product
    context_object_name = 'product'
    template_name = 'product.html'

    def get_context_data(self, **kwargs):
        """ 
        Метод для добавления дополнительной контекстной информации в шаблон.
        """
        Product.objects.filter(slug=self.kwargs['slug']).update(product_watched=F('product_watched') + 1)
        context = super().get_context_data(**kwargs)
        product = Product.objects.get(
            slug=self.kwargs['slug']
        )
        context['title'] = product.product_name
        products = (
            Product.objects
            .all()
            .exclude(slug=self.kwargs['slug'])
            .filter(product_category=product.product_category)
            [:3]
        )
        context['products'] = products

        return context


def login_registration(request):
    context = {
        'title': 'Войти или зарегистрироваться',
        'login_form': LoginForm,
        'registration_form': RegistrationForm
    }
    return render(
        request=request,
        template_name='registration.html',
        context=context
    )


def user_login(request):
    """ Аутентификация пользователя """
    form = LoginForm(
        data=request.POST
    )
    if form.is_valid():
        user = form.get_user()
        login(
            request=request,
            user=user
        )
        return redirect('index')
    else:
        messages.error(
            request=request,
            message='Неверное имя или пароль'
        )
        return redirect('user_registration')


def user_logout(request):
    """ Выход пользователя """
    logout(request=request)

    return redirect('index')


def registration(request):
    """ Регистрация пользователя """
    form = RegistrationForm(data=request.POST)
    if form.is_valid():
        form.save()
        messages.success(
            request=request,
            message='Аккаунт успешно создан'
        )
    else:
        # messages.error(request=request, message='Неверное имя или пароль')
        for error in form.errors:
            messages.error(
                request=request,
                message=form.errors[error].as_text()
            )

    return redirect('user_registration')


def save_favorite_product(request, product_slug):
    """
    Сохраняет или удаляет продукт из избранного пользователя.
    """
    if request.user.is_authenticated:
        user = request.user
        product = Product.objects.get(
            slug=product_slug
        )

        favorite_products = FavoriteProduct.objects.filter(
            user=user
        )

        if product in [item.product for item in favorite_products]:
            fav_product = FavoriteProduct.objects.get(
                user=user, product=product
            )
            fav_product.delete()
        else:
            FavoriteProduct.objects.create(
                user=user, product=product
            )

        page = request.META.get(
            'HTTP_REFERER',
            'category'
        )
        return redirect(page)
    else:
        return redirect('user_registration')


class FavoriteProductsView(LoginRequiredMixin, ListView):
    """
    Представление для отображения избранных продуктов пользователя.
    """
    model = FavoriteProduct
    context_object_name = 'products'
    template_name = 'favorites.html'
    login_url = 'user_registration'

    def get_queryset(self):
        """
        Получает набор данных для отображения.
        """
        favorites_products = FavoriteProduct.objects.filter(
            user=self.request.user
        )
        products = [item.product for item in favorites_products]

        return products


def cart(request):
    """
    Функция для отображения страницы корзины.
    """
    if request.user.is_authenticated:
        cart_info = get_cart_data(
            request=request
        )
        context = {
            'title': 'Корзина',
            'order': cart_info['order'],
            'order_products': cart_info['order_products'],
            'cart_total_quantity': cart_info['cart_total_quantity'],
        }
        return render(
            request=request,
            template_name='cart.html',
            context=context
        )
    else:
        return redirect('user_registration')


def to_cart(request, product_id, action):
    """
    Функция для добавления, удаления или полного удаления продукта из корзины.
    """
    if request.user.is_authenticated:
        CartForAuthenticatedUser(
            request=request,
            product_id=product_id,
            action=action
        )
        return redirect('cart')
    else:
        messages.error(
            request=request,
            message='Для совершения покупок, авторизуйтесь или зарегистрируйтесь'
        )
        return redirect('user_registration')


def checkout(request):
    """
    Отображение страницы оформления заказа.
    """
    cart_info = get_cart_data(
        request=request
    )
    context = {
        'title': 'Оформление заказа',
        'order': cart_info['order'],
        'order_products': cart_info['order_products'],
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'customer_form': CustomerForm(),
        'shipping_form': ShippingForm(),
    }

    return render(
        request=request,
        template_name='checkout.html',
        context=context
    )


def checkout_session(request):
    """
    Создаёт платёжную сессию Stripe для оформления заказа пользователя.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        user_cart = CartForAuthenticatedUser(
            request=request
        )
        cart_info = user_cart.get_cart_info()
        customer_form = CustomerForm(
            data=request.POST
        )
        if customer_form.is_valid():
            customer = Customer.objects.get(
                user=request.user
            )
            customer.first_name = customer_form.cleaned_data['first_name']
            customer.last_name = customer_form.cleaned_data['last_name']
            customer.email = customer_form.cleaned_data['email']
            customer.phone = customer_form.cleaned_data['phone']
            customer.save()

        shipping_form = ShippingForm(
            data=request.POST
        )
        if shipping_form.is_valid():
            address = shipping_form.save(
                commit=False
            )
            address.customer = Customer.objects.get(
                user=request.user
            )
            address.order = user_cart.get_cart_info()['order']
            address.save()

        total_price = cart_info['cart_total_price']
        total_quantity = cart_info['cart_total_quantity']

        session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'rub',
                        'product_data': {
                            'name': 'Покупка с магазина e-Shop'
                        },
                        'unit_amount': int(total_price * 100)
                    },
                    'quantity': total_quantity
                },
            ],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('success')),
        )

        return redirect(session.url, 303)

def success_payment(request):
    """
    Обрабатывает успешное завершение оплаты.
    """
    user_cart = CartForAuthenticatedUser(
        request=request
    )
    user_cart.clear()
    messages.success(
        request=request,
        message='Оплата прошла успешно'
    )

    return render(
        request=request,
        template_name='success.html'
    )
