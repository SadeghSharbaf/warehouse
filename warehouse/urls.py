from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('dashbord/', admin.site.urls),
    path('api/inventory/',include('inventory.api.urls')),
]
