from django.contrib import admin

from .models import Category, Product, Gallery, Order, OrderProduct, Customer, ShippingAddress


class GalleryInline(admin.TabularInline):
    """
    Вспомогательный класс для отображения изображений (Gallery) в виде встроенной формы
    на странице редактирования модели Product в админ-панели.
    """
    fk_name = 'product'
    model = Gallery
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    """
    Класс настройки админ-панели для модели Category.
    Позволяет управлять отображением и поведением категорий в админке.
    """
    list_display = (
        'category_name',
        'parent',
        'get_product_count',
    )
    prepopulated_fields = {
        'slug': ('category_name', ),
    }

    def get_product_count(self, obj):
        """
        Метод для подсчета количества товаров в текущей категории.
        Возвращает количество товаров, связанных с этой категорией.
        """
        return str(len(obj.products.all())) if obj.products else '0'

    get_product_count.short_description = 'Количество товаров'


class ProductAdmin(admin.ModelAdmin):
    """
    Класс настройки админ-панели для модели Product.
    Позволяет добавлять функциональность по отображению, редактированию и фильтрации продуктов.
    """
    list_display = (
        'pk',
        'product_name',
        'product_category',
        'product_quantity',
        'product_price',
        'product_created_at',
        'product_size',
        'product_color',
    )
    list_editable = (
        'product_price',
        'product_quantity',
        'product_size',
        'product_color',
    )
    prepopulated_fields = {
        'slug': ('product_name', ),
    }
    list_filter = (
        'product_name',
        'product_price',
    )
    list_display_links = (
        'pk',
        'product_name',
    )
    readonly_fields = (
        'product_watched',
    )
    inlines = (
        GalleryInline,
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Gallery)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(Customer)
admin.site.register(ShippingAddress)
