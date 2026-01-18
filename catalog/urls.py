from django.urls import path
from catalog.apps import CatalogConfig
from catalog.views import home, contacts, base, product_details

app_name = CatalogConfig.name

urlpatterns = [
    path('home/',home, name='home'),
    path('contacts/',contacts, name='contacts'),
    path('base/',base, name='base'),
    path('products/<int:pk>/', product_details, name='product_details'),
]
