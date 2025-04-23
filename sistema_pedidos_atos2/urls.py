from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('comandas/', include('comandas.urls')),
    path('caixa/', include('caixas.urls')),
]