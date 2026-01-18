from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from .models import BlogPost


class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog/blogpost_list.html'

    def get_queryset(self):
        # Выводим только статьи с положительным признаком публикации
        return super().get_queryset().filter(is_published=True)


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/blogpost_detail.html'

    def get_object(self, queryset=None):
        # Увеличиваем счетчик просмотров при каждом открытии
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj


class BlogPostCreateView(CreateView):
    model = BlogPost
    fields = ('title', 'content', 'preview', 'is_published')
    template_name = 'blog/blogpost_form.html'

    def get_success_url(self):
        # После создания перенаправляем на страницу созданной статьи
        return reverse('blog:blogpost_detail', kwargs={'pk': self.object.pk})


class BlogPostUpdateView(UpdateView):
    model = BlogPost
    fields = ('title', 'content', 'preview', 'is_published')
    template_name = 'blog/blogpost_form.html'

    def get_success_url(self):
        # После редактирования перенаправляем на страницу отредактированной статьи
        return reverse('blog:blogpost_detail', kwargs={'pk': self.object.pk})


class BlogPostDeleteView(DeleteView):
    model = BlogPost
    success_url = reverse_lazy('blog:blogpost_list')
    template_name = 'blog/blogpost_confirm_delete.html'