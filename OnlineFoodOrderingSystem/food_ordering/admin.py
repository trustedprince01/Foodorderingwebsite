from django.contrib import admin
from .models import Food, Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'food', 'quantity', 'total_price', 'ordered_at', 'status')
    list_filter = ('ordered_at', 'status')
    search_fields = ('user__username', 'food__name')
    list_editable = ('status',)
    
admin.site.register(Food)
admin.site.register(Order, OrderAdmin)
