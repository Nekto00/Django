from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .models import Product
from .forms import ProductForm


class OwnerRequiredMixin(UserPassesTestMixin):
    """Только владелец может редактировать"""

    def test_func(self):
        product = self.get_object()
        return product.owner == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, 'Только владелец может редактировать продукт!')
        raise PermissionDenied("Доступ запрещен")


class OwnerOrModeratorDeleteMixin(UserPassesTestMixin):
    """Владелец или модератор может удалять"""

    def test_func(self):
        product = self.get_object()
        user = self.request.user

        # Владелец может удалять
        if product.owner == user:
            return True

        # Модератор может удалять
        if user.has_perm('catalog.delete_product'):
            return True

        return False

    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав для удаления этого продукта!')
        raise PermissionDenied("Доступ запрещен")



# Общедоступные представления (не требуют авторизации)
class CatalogListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_authenticated:
            # Показываем все продукты владельцу
            # Или опубликованные + свои неопубликованные
            if user.has_perm('catalog.can_unpublish_product'):  # Модератор видит все
                return queryset

            # Обычный пользователь видит опубликованные + свои
            return queryset.filter(
                Q(is_published=True) |
                Q(owner=user)
            )

        # Анонимные пользователи видят только опубликованные
        return queryset.filter(is_published=True)


class CatalogDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj


# ЗАЩИЩЕННЫЕ представления (требуют авторизации)
class CatalogCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    login_url = '/users/login/'

    def form_valid(self, form):
        # Автоматически устанавливаем владельца
        form.instance.owner = self.request.user
        form.instance.is_published = False  # По умолчанию не опубликовано
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Продукт успешно создан!')
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})


class CatalogUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    login_url = '/users/login/'

    def get_success_url(self):
        messages.success(self.request, 'Продукт успешно обновлен!')
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})


# CatalogDeleteView - владелец ИЛИ модератор
class CatalogDeleteView(LoginRequiredMixin, OwnerOrModeratorDeleteMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('catalog:base')
    template_name = 'catalog/product_confirm_delete.html'
    login_url = '/users/login/'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Продукт успешно удален!')
        return super().delete(request, *args, **kwargs)


# Функции тоже защищаем если нужно
@login_required(login_url='/users/login/')
@permission_required('catalog.can_unpublish_product', raise_exception=True)
def unpublish_product(request, pk):
    """Отмена публикации продукта (только для модераторов)"""
    product = get_object_or_404(Product, pk=pk)

    if product.is_published:
        product.is_published = False
        product.save()
        messages.success(request, f'Публикация продукта "{product.name}" отменена!')
    else:
        messages.warning(request, 'Продукт уже не опубликован!')

    return redirect('catalog:product_detail', pk=product.pk)



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

