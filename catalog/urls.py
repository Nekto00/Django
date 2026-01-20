from django.urls import path
from catalog.apps import CatalogConfig
from catalog.views import HomeView, ContactsView, CatalogListView, CatalogDetailView, CatalogCreateView, UpdateView, \
    CatalogUpdateView, CatalogDeleteView

app_name = CatalogConfig.name

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('base/',CatalogListView.as_view(), name='base'),
    path('products/<int:pk>/', CatalogDetailView.as_view(), name='product_detail'),
    path('create/', CatalogCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/update/', CatalogUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', CatalogDeleteView.as_view(), name='product_delete'),
]
