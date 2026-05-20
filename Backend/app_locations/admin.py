from django.contrib import admin
from .models import Location

# Register your models here.

  

class LocationAdmin(admin.ModelAdmin):
  list_display = ("staddr", "city", "state", "hno", "landmark")
  search_fields = ("staddr", "hno", "landmark")
  list_filter = ("city", "state")

admin.site.register(Location, LocationAdmin)
