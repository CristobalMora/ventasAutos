from django import forms
from .models import Cliente
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import CustomUser, Producto, CartItem




class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())

class ContactForm(forms.Form):
    name = forms.CharField(label='Nombre', max_length=100)
    email = forms.EmailField(label='Email')
    message = forms.CharField(label='Mensaje', widget=forms.Textarea)

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'año', 'precio', 'imagen', 'stock']       

class AddToCartForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']

class RangoFechasForm(forms.Form):
    fecha_inicio = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    fecha_fin = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
        