# posts/forms.py
from django.forms import ModelForm
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = (
            'text',
            'group',
            'image',
        )
        labels = {
            'text': 'Текст',
            'group': 'группа',
            'image': 'картинка',
        }
        help_texts = {
            'text': ('Напишите текст поста,'
                     ' обязателен для заполнения'),
            'group': ('Выбор группы поста,'
                      ' можно оставить пустым'),
            'image': 'Можно прикрепить картинку',
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Комментарий:'}
        help_texts = {
            'text': ('Напишите текст комментария,'
                     ' обязателен для заполнения'),
        }
