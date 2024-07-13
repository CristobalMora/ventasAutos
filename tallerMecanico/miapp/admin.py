from django.contrib import admin
from .models import Producto

# Register your models here.
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email')  # Campos a mostrar en la lista de clientes
    search_fields = ('nombre', 'email')

# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Producto)
