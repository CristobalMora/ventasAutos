
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from miapp import views 
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login_view'),
    path('contacto/', views.contacto, name='contacto'),
    path('producto/', views.producto, name='producto'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('custom_login/', views.CustomLoginView.as_view(), name='custom_login'),
    path('registrar_producto/', views.registrar_producto, name='registrar_producto'),
    path('lista_productos/', views.lista_productos, name='lista_productos'),  # Asegúrate de que esta línea esté presente
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('product_list/', views.product_list, name='product_list'),
    path('edit_product/', views.edit_product, name='edit_product'),
    path('reporte_ventas/', views.reporte_ventas, name='reporte_ventas'),
    path('descargar-reporte-ventas/', views.descargar_reporte_ventas, name='descargar_reporte_ventas'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.conf import settings
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)