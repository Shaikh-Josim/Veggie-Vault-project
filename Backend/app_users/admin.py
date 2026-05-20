from django.contrib import admin
from django.utils.html import format_html
from .models import User, Profile
# Register your models here.

class ProfileInline(admin.StackedInline):
  model = Profile


class UserAdmin(admin.ModelAdmin):
  list_display = ("email",)
  search_fields = ("email",)
  inlines = [ProfileInline]
  

@admin.action(description="Make selected Admins")
def make_admin(modeladmin, request, queryset):
    queryset.update(role=1)

@admin.action(description="Make selected Workers")
def make_worker(modeladmin, request, queryset):
    queryset.update(role=2)

@admin.action(description="Make selected Consumers")
def make_consumer(modeladmin, request, queryset):
    queryset.update(role=3)

class ProfileAdmin(admin.ModelAdmin):
  list_display = ("fname", "lname", "get_email", "role", "mobile_no", "user_Img", "get_staddr", "get_city", "get_state", "get_hno", "get_landmark", "preview_img")
  list_select_related = ("user","location")
  list_filter = ( "role", )
  search_fields = ("fname", "lname", "mobile_no")
  actions = [make_admin, make_consumer, make_worker]
  

  @admin.display(ordering="email", description="Email")
  def get_email(self, obj):
    return obj.user.email
  
  @admin.display(ordering="staddr", description="Street Address")
  def get_staddr(self, obj):
    return obj.location.staddr
  
  @admin.display(ordering="city", description="City")
  def get_city(self, obj):
    return obj.location.city
  
  @admin.display(ordering="state", description="State")
  def get_state(self, obj):
    return obj.location.state
  
  @admin.display(ordering="hno", description="House no")
  def get_hno(self, obj):
    return obj.location.hno
  
  @admin.display(ordering="landmark", description="Landmark")
  def get_landmark(self, obj):
    return obj.location.landmark
  
  def preview_img(self, obj):
    if obj and obj.user_Img: 
      return format_html(
          '<img src="{}" style="max-height:100px; max-width:100px;" />',
          obj.user_Img.url
      )
        
    return "No image"
  
  preview_img.short_description = "Image"
  

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
