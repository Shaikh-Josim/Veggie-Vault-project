from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Cart

# Register your models here.

@admin.action(description="Make selected Vegetable")
def set_vegetable_category(modeladmin, request, queryset):
    queryset.update(category=1)

@admin.action(description="Make selected Fruit")
def set_fruit_category(modeladmin, request, queryset):
    queryset.update(category=2)

@admin.action(description="Make selected in stock")
def set_status_instock(modeladmin, request, queryset):
    queryset.update(status=1)

@admin.action(description="Make selected out of stock")
def set_status_outofstock(modeladmin, request, queryset):
    queryset.update(status=2)

class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "discription", "price", "stock", "status", "product_Img", "preview_img")
    search_fields = ("name", "price")
    list_filter = ("category", "stock", "status")
    actions = [set_vegetable_category, set_fruit_category, set_status_instock, set_status_outofstock]
  

    def preview_img(self, obj):
        if obj and obj.product_Img: 
            return format_html(
                '<img src="{}" style="max-height:100px; max-width:100px;" />',
                obj.product_Img.url
            )
        
        return "No image"
  
    preview_img.short_description = "Image"
    

admin.site.register(Product, ProductAdmin)
