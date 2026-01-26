from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Product
from .forms import ProductForm


class CatalogListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'


class CatalogDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        return context


class CatalogCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Продукт успешно создан!')
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class CatalogUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Продукт успешно обновлен!')
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class CatalogDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('catalog:base')
    template_name = 'catalog/product_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Продукт успешно удален!')
        return super().delete(request, *args, **kwargs)


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

