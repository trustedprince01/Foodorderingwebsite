from django.contrib import admin
from .models import Food, Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "food", "quantity", "status", "ordered_at")
    list_filter = ("status",)
    search_fields = ("user__username", "food__name")
    list_editable = ("status",)  # Allows editing status directly in admin panel
    
admin.site.register(Food)
admin.site.register(Order, OrderAdmin)
