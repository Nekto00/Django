from itertools import product

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView,DeleteView
from django.urls import reverse_lazy
from catalog.models import Product

class CatalogListView(ListView):
    model = Product

class CatalogDetailView(DetailView):
    model = Product

class CatalogCreateView(CreateView):
    model = Product
    fields = ('name','category','price', 'photo','created_at')
    success_url = reverse_lazy('catalog:base')

class CatalogUpdateView(UpdateView):
    model = Product
    fields = ('name', 'category', 'price', 'photo', 'created_at')
    success_url = reverse_lazy('catalog:base')

class CatalogDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('catalog:base')


def home(request):
    return render(request, 'home.html')

def contacts(request):
    return render(request, 'contacts.html')


