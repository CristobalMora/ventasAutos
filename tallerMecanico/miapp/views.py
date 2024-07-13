from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.views import LoginView
from .forms import LoginForm, ContactForm, CustomUserCreationForm, ProductoForm, AddToCartForm, RangoFechasForm
from django.contrib import messages
from .models import Cart, CartItem, Producto, Order
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime 
# Create your views here.

def index(request):
    return render(request, 'index.html', {'year': 2024})


from django.shortcuts import redirect

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                # Redirigir según el tipo de usuario
                if user.is_staff:
                    return redirect('registrar_producto')
                else:
                    return redirect('producto')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def contacto(request):
    form = ContactForm()
    return render(request, 'contacto.html', {'form': form})


def producto(request):
    productos = Producto.objects.all()
    return render(request, 'producto.html', {'productos': productos})

class CustomLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('producto')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('product_list') 
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

def registrar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')  
    else:
        form = ProductoForm()
    return render(request, 'registrar_producto.html', {'form': form})

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Producto, id=product_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=product)
    return render(request, 'edit_product.html', {'form': form})

def lista_productos(request):
    if request.method == 'POST':
        if 'actualizar' in request.POST:
            producto_id = request.POST.get('producto_id')
            producto = get_object_or_404(Producto, id=producto_id)
            form = ProductoForm(request.POST, request.FILES, instance=producto)
            if form.is_valid():
                form.save()
                return redirect('lista_productos')

        elif 'borrar' in request.POST:
            producto_id = request.POST.get('producto_id')
            producto = get_object_or_404(Producto, id=producto_id)
            producto.delete()
            return redirect('lista_productos')

    productos = Producto.objects.all()
    forms = {producto.id: ProductoForm(instance=producto) for producto in productos}
    return render(request, 'lista_productos.html', {'productos': productos, 'forms': forms})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Producto, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if request.method == 'POST':
        form = AddToCartForm(request.POST, instance=cart_item)
        if form.is_valid():
            form.save()
            return redirect('cart_detail')
    else:
        form = AddToCartForm(instance=cart_item)
    
    return render(request, 'add_to_cart.html', {'form': form, 'product': product})


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart_detail.html', {'cart': cart})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart_detail')

@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        # Si no hay carrito, redirigir a la página del carrito
        return redirect('cart_detail')
    
    order = Order.objects.create(user=request.user, total=cart.get_total())
    for item in cart.items.all():
        order.items.add(item)
        product = item.product
        if product.stock >= item.quantity:  # Verificar si hay suficiente stock
            product.stock -= item.quantity  # Disminuir la cantidad del producto en el stock
            product.save()  # Guardar los cambios en la base de datos
            item.delete()  # Eliminar el item del carrito
        else:
            # Manejar el caso donde no hay suficiente stock
            # Redirigir a una página de error o mostrar un mensaje
            return render(request, 'cart_detail.html', {'error': 'No hay suficiente stock para algunos productos.'})
    
    cart.delete()  # Eliminar el carrito después de procesar la compra
    return render(request, 'checkout.html', {'order': order})
    
@login_required
def product_list(request):
    productos = Producto.objects.all()
    return render(request, 'product_list.html', {'productos': productos})

@login_required
def reporte_ventas(request):
    ventas = None
    if request.method == 'POST':
        form = RangoFechasForm(request.POST)
        if form.is_valid():
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']

            # Convertir las fechas a objetos datetime con zona horaria
            fecha_inicio = timezone.make_aware(timezone.datetime.combine(fecha_inicio, timezone.datetime.min.time()))
            fecha_fin = timezone.make_aware(timezone.datetime.combine(fecha_fin, timezone.datetime.max.time()))

            ventas = Order.objects.filter(created_at__range=[fecha_inicio, fecha_fin])
    else:
        form = RangoFechasForm()

    return render(request, 'reporte_ventas.html', {'form': form, 'ventas': ventas})

@login_required
def descargar_reporte_ventas(request):
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    
    # Convertir las cadenas de fechas a objetos datetime
    fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
    fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
    
    # Asegurar que las fechas sean conscientes de la zona horaria
    fecha_inicio = timezone.make_aware(fecha_inicio, timezone.get_current_timezone())
    fecha_fin = timezone.make_aware(fecha_fin, timezone.get_current_timezone())

    ventas = Order.objects.filter(created_at__range=[fecha_inicio, fecha_fin])

    # Generar PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.alignment = 1  # Centered
    normal_style = styles['Normal']
    header_style = ParagraphStyle(name='HeaderStyle', parent=styles['Heading1'], alignment=1, fontSize=14)

    # Elementos del PDF
    elements = []

    # Título
    elements.append(Paragraph(f"Reporte de Ventas", title_style))
    elements.append(Paragraph(f"Desde: {fecha_inicio_str} Hasta: {fecha_fin_str}", normal_style))
    elements.append(Paragraph("<br/><br/>", normal_style))

    # Tabla de Items
    data = [['Usuario', 'Total', 'Fecha de Creación']]
    for venta in ventas:
        data.append([
            venta.user.username,
            f"${venta.total:.2f}",
            venta.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    table = Table(data, colWidths=[2 * inch, 2 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Construir el documento
    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.pdf"'
    return response