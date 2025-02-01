from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Food, Order
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.conf import settings

@staff_member_required
def manage_food(request):
    return redirect('/admin/food_ordering/food/')


@login_required

def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    return render(request, 'food_ordering/order_history.html', {'orders': orders})

def order_food(request, food_id):
    food = get_object_or_404(Food, id=food_id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        Order.objects.create(user=request.user, food=food, quantity=quantity)
        return redirect("order_history")  # Redirect after confirming order

    return render(request, "food_ordering/checkout.html", {
        "food": food,
        "PAYSTACK_PUBLIC_KEY": settings.PAYSTACK_PUBLIC_KEY  # Send key to template
    })


def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "food_ordering/login.html", {"form": form})


def home(request):
    return render(request, 'food_ordering/home.html')

def payment_success(request):
    reference = request.GET.get("reference", "")
    return render(request, "food_ordering/payment_success.html", {"reference": reference})


def menu(request):
    foods = Food.objects.all()  # Fetch all food items
    return render(request, 'food_ordering/menu.html', {'foods': foods})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in after signup
            return redirect("home")  # Redirect to homepage
    else:
        form = RegisterForm()
    return render(request, "food_ordering/register.html", {"form": form})

def user_logout(request):
    logout(request)
    return redirect("home")