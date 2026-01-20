from itertools import product

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView,DeleteView, TemplateView
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


class HomeView(TemplateView):
    """Главная страница"""
    template_name = 'catalog/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        # Можно добавить дополнительные данные, например, последние продукты
        context['latest_products'] = Product.objects.all().order_by('-created_at')[:3]
        return context


class ContactsView(TemplateView):
    """Страница контактов"""
    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Контакты'

        # Пример данных контактов (можно вынести в настройки или БД)
        context['contacts'] = [
            {'name': 'Телефон', 'value': '+7 (999) 123-45-67', 'icon': 'telephone'},
            {'name': 'Email', 'value': 'info@catalog.ru', 'icon': 'envelope'},
            {'name': 'Адрес', 'value': 'г. Москва, ул. Примерная, д. 1', 'icon': 'geo-alt'},
            {'name': 'Режим работы', 'value': 'Пн-Пт: 9:00-18:00', 'icon': 'clock'},
        ]

        # Обработка POST запроса для формы обратной связи
        if self.request.method == 'POST':
            context['form_submitted'] = True
            context['message'] = 'Спасибо! Ваше сообщение отправлено.'

        return context

    def post(self, request, *args, **kwargs):
        """Обработка POST запроса (форма обратной связи)"""
        # Здесь можно добавить логику обработки формы
        # Например, сохранение в БД или отправку email
        return self.get(request, *args, **kwargs)

