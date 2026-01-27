from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.views import View
from django.contrib.auth import logout
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .forms import UserRegisterForm, UserLoginForm
from .models import User


class UserRegisterView(CreateView):
    """Регистрация нового пользователя"""
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        """Обработка успешной регистрации с отправкой приветственного письма"""
        response = super().form_valid(form)

        # Отправка приветственного письма
        self.send_welcome_email(form.instance)

        # Сообщение пользователю
        messages.success(
            self.request,
            'Регистрация прошла успешно! Проверьте вашу почту для приветственного письма.'
        )

        return response

    def send_welcome_email(self, user):
        """Отправка приветственного письма"""
        subject = 'Добро пожаловать в наш каталог!'

        # HTML версия письма
        html_message = render_to_string('users/emails/welcome_email.html', {
            'user': user,
            'site_name': 'Каталог товаров'
        })

        # Текстовая версия письма
        plain_message = strip_tags(html_message)

        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=None,  # Используется DEFAULT_FROM_EMAIL из settings
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            # Логируем ошибку, но не прерываем регистрацию
            print(f"Ошибка отправки email: {e}")


class UserLoginView(LoginView):
    """Авторизация пользователя"""
    form_class = UserLoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        messages.success(self.request, f'Добро пожаловать, {self.request.user.email}!')
        return reverse_lazy('catalog:base')

    def form_invalid(self, form):
        messages.error(self.request, 'Неверный email или пароль.')
        return super().form_invalid(form)


class UserLogoutView(View):
    """Простой выход с GET запросом"""

    def get(self, request):
        """Выход по GET запросу (из ссылки)"""
        if request.user.is_authenticated:
            logout(request)
            messages.info(request, 'Вы успешно вышли из системы.')
        return redirect('catalog:base')

    def post(self, request):
        """Выход по POST запросу (из формы)"""
        return self.get(request)


class UserProfileView(LoginRequiredMixin, FormView):
    """Профиль пользователя (дополнительно)"""
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_form_class(self):
        from users.forms import UserUpdateForm  # Импортируем тут, чтобы избежать циклического импорта
        return UserUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)


