from django import forms
from django.core.exceptions import ValidationError
from .models import Product

FORBIDDEN_WORDS = [
    'казино', 'криптовалюта', 'крипта', 'биржа',
    'дешево', 'бесплатно', 'обман', 'полиция', 'радар'
]


class ProductForm(forms.ModelForm):
    agree_to_terms = forms.BooleanField(
        label="Я согласен с условиями публикации",
        required=True,
        help_text="Необходимо подтвердить согласие с правилами",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    notify_me = forms.BooleanField(
        label="Уведомлять об изменениях",
        required=False,
        initial=True,
        help_text="Получать уведомления на email об изменениях продукта",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Product
        exclude = ['owner', 'updated_at', 'views_count', 'is_published']
        fields = ('name', 'category', 'description', 'price', 'photo', 'created_at')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'created_at': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """Инициализация формы с учетом существующих объектов"""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['agree_to_terms'].required = False
            self.fields['agree_to_terms'].initial = True

    def _check_forbidden_words(self, text, field_name):
        """Проверка на запрещенные слова в тексте"""
        if text:
            text_lower = text.lower()
            for word in FORBIDDEN_WORDS:
                if word in text_lower:
                    raise ValidationError(
                        f'Нельзя использовать запрещенное слово "{word}"'
                    )

    def clean_name(self):
        """Валидация названия продукта на запрещенные слова"""
        name = self.cleaned_data.get('name', '')
        self._check_forbidden_words(name, 'name')
        return name

    def clean_description(self):
        """Валидация описания продукта на запрещенные слова"""
        description = self.cleaned_data.get('description', '')
        self._check_forbidden_words(description, 'description')
        return description

    def clean_price(self):
        """Валидация цены (не может быть отрицательной)"""
        price = self.cleaned_data.get('price')

        if price is not None and price < 0:
            raise ValidationError('Цена не может быть отрицательной')

        return price

    def clean_agree_to_terms(self):
        """Валидация чекбокса согласия (только для создания)"""
        agree = self.cleaned_data.get('agree_to_terms')

        if not self.instance.pk and not agree:
            raise ValidationError('Вы должны согласиться с условиями публикации')

        return agree