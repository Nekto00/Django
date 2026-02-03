from django.urls import path
from catalog.apps import CatalogConfig
from catalog.views import HomeView, ContactsView, CatalogListView, CatalogDetailView, CatalogCreateView, UpdateView, \
    CatalogUpdateView, CatalogDeleteView, unpublish_product, CategoryProductsView

app_name = CatalogConfig.name

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('base/',CatalogListView.as_view(), name='base'),
    path('products/<int:pk>/', CatalogDetailView.as_view(), name='product_detail'),
    path('create/', CatalogCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/update/', CatalogUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', CatalogDeleteView.as_view(), name='product_delete'),
    path('products/<int:pk>/unpublish/', unpublish_product, name='product_unpublish'),
    path('category/<slug:category_slug>/', CategoryProductsView.as_view(), name='category_products'),
]
