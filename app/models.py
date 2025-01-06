from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


DEFAULT_IMAGE = 'https://stilsoft.ru/images/catalog/noup.png'


class Category(models.Model):
    """ Модель категории в базе данных """
    category_name = models.CharField(
        max_length=150,
        verbose_name='Наименование категории',
    )
    category_image = models.ImageField(
        upload_to='categories/',
        null=True,
        blank=True,
        verbose_name='Изображение',
    )
    slug = models.SlugField(
        unique=True,
        null=True,
    )
    parent = models.ForeignKey(
        to='self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Категория',
        related_name='subcategories',
    )

    def __str__(self):
        """Используется для человекочитаемого представления объекта."""
        return self.category_name

    def __repr__(self):
        """Используется для технического представления объекта."""
        return f'Категория pk={self.pk}, name={self.category_name}'

    def get_category_image(self):
        """
        Метод для получения URL изображения категории.
        Если изображение отсутствует, возвращается изображение по умолчанию.
        """
        return self.category_image.url if self.category_image else DEFAULT_IMAGE

    def get_absolute_url(self):
        """
        Метод для получения абсолютного URL объекта.
        Возвращает ссылку на детальную страницу категории на основе её slug.
        """
        # Используем функцию reverse для построения URL по имени маршрута 'category_detail'
        # Передаем параметр 'slug', который берется из текущего объекта (self.slug)
        return reverse('category', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Категорию'
        verbose_name_plural ='Категории'


class Product(models.Model):
    """ Модель продукта в базе данных """
    product_name = models.CharField(
        max_length=255,
        verbose_name='Наименование товара',
    )
    product_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена товара',
    )
    product_created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    product_watched = models.IntegerField(
        default=0,
        verbose_name='Просмотры',
    )
    product_quantity = models.IntegerField(
        default=0,
        verbose_name='Количество на складе',
    )
    product_description = models.TextField(
        default='Здесь скоро будет описание...',
        verbose_name='Описание товара',
    )
    product_info = models.TextField(
        default='Дополнительная информация о товаре',
        verbose_name='Информация о товаре',
    )
    product_category = models.ForeignKey(
        to=Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='products',
    )
    slug = models.SlugField(
        unique=True,
        null=True,
    )
    product_size = models.FloatField(
        default=0,
        verbose_name='Размер',
        null=True,
        blank=True,
    )
    product_color = models.CharField(
        max_length=30,
        default='Черный',
        verbose_name='Цвет',
    )

    def __str__(self):
        """Используется для человекочитаемого представления объекта."""
        return self.product_name

    def __repr__(self):
        """Используется для технического представления объекта."""
        return f'Товар: pk={self.pk}, name={self.product_name} price={self.product_price}'

    def get_first_image(self):
        """
        Метод для получения URL первого изображения из связанных изображений продукта.
        Если изображений нет, возвращает изображение по умолчанию.
        """
        first_image = self.images.first() 
        return first_image.image.url if first_image else DEFAULT_IMAGE

    def get_absolute_url(self):
        """
        Возвращает абсолютный URL для объекта модели.

        Этот метод является стандартным соглашением в Django для определения
        канонического URL объекта. Он используется, например, в админ-панели
        и может быть полезен в шаблонах и других частях кода.
        """
        return reverse('product', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Gallery(models.Model):
    """ Модель изображений продукта в базе данных """
    image = models.ImageField(
        upload_to='products/',
        verbose_name='Изображение',
    )
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name='images',
    )

    def __str__(self):
        """ Строковое представление объекта """
        return f"Изображение для {self.product}"

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Галерея'


class FavoriteProduct(models.Model):
    """
    Модель "Избранный товар", связывает пользователей с их избранными товарами.
    """
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        verbose_name='Товар',
    )

    def __str__(self):
        """
        Метод для получения строкового представления объекта модели.
        """
        return self.product.product_name

    class Meta:
        """
        Мета-класс для настройки модели.
        """
        verbose_name = 'Избранный товар'
        verbose_name_plural = 'Извранные товары'


class Customer(models.Model):
    """
    Модель для представления покупателя в системе.
    """
    user = models.OneToOneField(
        to=User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Пользователь',
    )
    first_name = models.CharField(
        max_length=255,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name='Фамилия',
    )
    email = models.EmailField(
        verbose_name='Почта',
    )
    phone = models.CharField(
        max_length=255,
        verbose_name='Контактный номер',
    )

    def __str__(self):
        """
        Возвращает строковое представление объекта Customer.
        """
        return self.first_name

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'



class Order(models.Model):
    """
    Модель для представления заказа в системе.
    """
    customer = models.ForeignKey(
        to=Customer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Пользователь',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан',
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name='Завершен',
    )
    shipping = models.BooleanField(
        default=True,
        verbose_name='Доставка',
    )

    def __str__(self):
        """
        Возвращает строковое представление объекта Order.
        """
        return str(self.pk)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    @property
    def get_cart_total_price(self):
        """
        Возвращает общую стоимость корзины заказа.
        """
        return sum([product.get_total_price for product in self.ordered.all()])

    @property
    def get_cart_total_quantity(self):
        """
        Возвращает общее количество товаров в корзине.
        """
        return sum([product.quantity for product in self.ordered.all()])


class OrderProduct(models.Model):
    """
    Модель для представления товара в заказе.
    """
    product = models.ForeignKey(
        to=Product,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Наименование товара',
    )
    order = models.ForeignKey(
        to=Order,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ordered',
        verbose_name='Заказ',
    )
    quantity = models.IntegerField(
        default=0,
        blank=True,
        null=True,
        verbose_name='Количество товаров',
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления',
    )

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    @property
    def get_total_price(self):
        """
        Вычисляет общую стоимость данного товара в заказе.
        """
        return self.product.product_price * self.quantity


class ShippingAddress(models.Model):
    """Модель для хранения информации об адресе доставки."""
    customer = models.ForeignKey(
        to='Customer',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Пользователь',
    )
    order = models.ForeignKey(
        to='Order',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Заказ',
    )
    city = models.CharField(
        max_length=255,
        verbose_name='город',
    )
    state = models.CharField(
        max_length=255,
        verbose_name='район',
    )
    street = models.CharField(
        max_length=255,
        verbose_name='улица',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        """Возвращает строковое представление объекта (название улицы)."""
        return self.street

    class Meta:
        """Метаданные для модели."""
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставки'
