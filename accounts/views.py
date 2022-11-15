from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from django.contrib import messages

from .models import *
from .forms import OrderForm, CreateUserForm, CustomerForm
from .filters import OrderFilter
from .decorators import unauthenticated_user, allowed_users, admin_only

# Create your views here.

@unauthenticated_user
def register_page(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            
            messages.success(request, "Accout created for " + username)
            return redirect('login')

    context = {
        'form': form,
    }
    return render(request, 'register.html', context)

@unauthenticated_user
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')

        else:
            messages.info(request, "Username or Password is incorrect")

    context = {}
    return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_customers = customers.count()
    total_orders = orders.count()

    total_orders_delivered = orders.filter(status='Delivered').count()
    total_orders_pending = orders.filter(status='Pending').count()
    total_out_for_delivery = orders.filter(status='Out for delivery').count()

    context = {
        'orders': orders,
        'customers': customers,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'total_orders_delivered': total_orders_delivered,
        'total_orders_pending': total_orders_pending,
        'total_out_for_delivery': total_out_for_delivery,
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Customer'])
def user_page(request):
    orders = request.user.customer.order_set.all()

    total_orders = orders.count()

    total_orders_delivered = orders.filter(status='Delivered').count()
    total_orders_pending = orders.filter(status='Pending').count()
    total_out_for_delivery = orders.filter(status='Out for delivery').count()

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'total_orders_delivered': total_orders_delivered,
        'total_orders_pending': total_orders_pending,
        'total_out_for_delivery': total_out_for_delivery,
    }
    return render(request, 'user.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Customer'])
def account_settings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
    context = {
        'form': form,
    }
    return render(request, 'account_settings.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def product(request):
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'products.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def customer(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    orders_count = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context = {
        'customer': customer,
        'orders': orders,
        'orders_count': orders_count,
        'myFilter': myFilter,
    }
    return render(request, 'customers.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def create_order(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5)
    customer = Customer.objects.get(id=pk)
    form_set = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    # form = OrderForm(initial={'customer':customer})
    if request.method == 'POST':
        # form = OrderForm(request.POST)
        form_set = OrderFormSet(request.POST, instance=customer)
        if form_set.is_valid():
            form_set.save()
            return redirect('/')

    context = {
        'form_set': form_set,
        'title': 'Create Order',
        'customer': customer,
    }
    return render(request, 'order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def update_order(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {
        'form': form,
        'title': 'Update Order',
    }
    return render(request, 'order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['Admin'])
def delete_order(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')

    context = {'item': order}
    return render(request, 'delete.html', context)

