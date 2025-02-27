from django.contrib import admin
from . models import Product, Customer, Cart, Payment, OrderPlaced, Wishlist
from django.utils.html import format_html
from django.urls import reverse

# Register your models here.

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id','title','discounted_price','category','product_image']

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','locality','city','state','zipcode']

@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','product','quantity']
    def product(self, obj):
        link = reverse("admin:app_product_change", args=[obj.product.pk])
        return format_html('&lt;a href="{}"&gt;{}&lt;/a&gt;', link, obj.product.title)

@admin.register(Payment)
class Payment(admin.ModelAdmin):
    list_display = ['id','user','amount','razorpay_order_id','razorpay_payment_status','razorpay_payment_id','paid']

@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','customer','product','quantity','ordered_date','status','payment']

    def customer(self, obj):
        link = reverse("admin:app_customer_change", args=[obj.customer.pk])
        return format_html('&lt;a href="{}"&gt;{}&lt;/a&gt;', link, obj.customer.name)
    
    def product(self, obj):
        link = reverse("admin:app_product_change", args=[obj.product.pk])
        return format_html('&lt;a href="{}"&gt;{}&lt;/a&gt;', link, obj.product.title)
    

@admin.register(Wishlist)
class WishlistModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','product']
    def product(self, obj):
        link = reverse("admin:app_product_change", args=[obj.product.pk])
        return format_html('&lt;a href="{}"&gt;{}&lt;/a&gt;', link, obj.product.title)