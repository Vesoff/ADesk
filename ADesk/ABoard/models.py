from ckeditor.fields import RichTextField
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    TYPE = (('tanks', 'Танки'),
           ('healers', 'Хилы'),
           ('damage_dealers', 'ДД'),
           ('merchants', 'Торговцы'),
           ('gildmasters', 'Гилдмастеры'),
           ('quest_givers', 'Квестгиверы'),
           ('blacksmiths', 'Кузнецы'),
           ('tanners', 'Кожевники'),
           ('potion_makers', 'Зельевары'),
           ('spell_masters', 'Мастера заклинаний'))
    post_type = models.CharField(max_length=15, choices=TYPE, verbose_name='Категория')
    time_in = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, verbose_name='Название объявления')
    text = RichTextField()

    def get_absolute_url(self):
        return reverse('boardpost_detail', args=[str(self.id)])


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
