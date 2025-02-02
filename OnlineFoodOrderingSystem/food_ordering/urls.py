from django.urls import path
from . import views

urlpatterns = [
   path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),  # ✅ Make sure this exists
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('order/<int:food_id>/', views.order_food, name='order_food'),
    path('order-history/', views.order_history, name='order_history'),
    path('manage-food/', views.manage_food, name='manage_food'),
    path('payment-success/', views.payment_success, name='payment_success'),





]

