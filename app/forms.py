from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


from .models import User, Customer, ShippingAddress


class LoginForm(AuthenticationForm):
    """ Форма аутентификации пользователя """
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Имя пользователя',
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Пароль',
            }
        )
    )


class RegistrationForm(UserCreationForm):
    """ Форма регистрации пользователя """
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Пароль',
            }
        ),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Подтвердите пароль',
            }
        )
    )


    class Meta:
        model = User
        fields = (
            'username', 'email',
        )
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Имя пользователя',
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Почта',
                }
            ),
        }


class CustomerForm(forms.ModelForm):
    """
    Форма для создания или редактирования информации о покупателе.
    """
    class Meta:
        """
        Метаданные для настройки формы, связанной с моделью.
        """
        model = Customer
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone',
        )
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Имя',
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Фамилия',
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'example@example.com',
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '+79999999999',
                }
            ),
        }


class ShippingForm(forms.ModelForm):
    """
    Форма для ввода адреса доставки.
    """
    class Meta:
        """
        Метаданные для настройки формы, связанной с моделью.
        """

        model = ShippingAddress
        fields = (
            'city',
            'state',
            'street',  # Поле для улицы
        )
        widgets = {
            'city': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'город',
                }
            ),
            'state': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'район',
                }
            ),
            'street': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'улица, дом, квартира',
                }
            ),
        }
