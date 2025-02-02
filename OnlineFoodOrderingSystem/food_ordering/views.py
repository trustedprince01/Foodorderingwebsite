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
from django.core.mail import send_mail
from .models import Order 
import requests 

@staff_member_required
def manage_food(request):
    return redirect('/admin/food_ordering/food/')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    print("📝 Orders found:", orders)  # Debug message
    return render(request, 'food_ordering/order_history.html', {'orders': orders})

@login_required
def order_food(request, food_id):
    food = get_object_or_404(Food, id=food_id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))

        # ✅ Save food_id and quantity in session (DO NOT save order yet)
        request.session["food_id"] = food_id
        request.session["quantity"] = quantity

        print("✅ Food & Quantity Stored in Session:", food_id, quantity)  # Debug message

        # Redirect to checkout page (which opens Paystack)
        return redirect("checkout", food_id=food_id)

    return render(request, "food_ordering/checkout.html", {
        "food": food,
        "PAYSTACK_PUBLIC_KEY": settings.PAYSTACK_PUBLIC_KEY
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

    # ✅ Verify payment with Paystack
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }
    response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    result = response.json()

    if result["status"] and result["data"]["status"] == "success":
        # ✅ Retrieve food ID and quantity from session
        food_id = request.session.get("food_id")
        quantity = request.session.get("quantity", 1)

        if not food_id:
            messages.error(request, "Payment verified but no food order found.")
            return redirect("menu")

        food = get_object_or_404(Food, id=food_id)

        # ✅ Save the order in the database now that payment is confirmed
        order = Order.objects.create(
            user=request.user,
            food=food,
            quantity=quantity,
            status="Pending"
        )

        # ✅ Remove session data to prevent duplicate orders
        del request.session["food_id"]
        del request.session["quantity"]

        print("✅ Order saved after payment:", order)  # Debug message

        return render(request, "food_ordering/payment_success.html", {"reference": reference})

    else:
        messages.error(request, "Payment verification failed. Please try again.")
        return redirect("menu")


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

def send_order_email(user, order):
    subject = "Order Confirmation"
    message = f"""
    Hello {user.username},

    Your order for {order.food.name} (x{order.quantity}) has been received.
    Total: ${order.total_price}

    Thank you for ordering!
    """
    recipient_list = [user.email]

    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)