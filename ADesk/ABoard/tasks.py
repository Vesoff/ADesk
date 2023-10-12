from celery import shared_task
from django.contrib.auth.models import User
from .models import Post, Comment
from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone


@shared_task
def send_mail_monday_8am():
    now = timezone.now()
    weekly_posts = list(Post.objects.filter(time_in__gte=now - timedelta(days=7)))
    if weekly_posts:
        for user in User.objects.filter():
            print(user)
            list_posts = ''
            for post in weekly_posts:
                list_posts += f'\n{post.title}\nhttp://127.0.0.1:8000/board/{post.id}'
            send_mail(
                subject=f'ABoard - BEST MMORPG Looking for Help Hub: посты за прошедшую неделю.',
                message=f'Доброе утро, {user.username}!\nПредлагаем Вам ознакомиться с новыми объявлениями, '
                        f'появившимися за последние 7 дней:\n{list_posts}',
                from_email='aboard.vesoff@outlook.com',
                recipient_list=[user.email, ],
            )


@shared_task
def comment_send_email(comment_id):
    comment = Comment.objects.get(id=comment_id)
    send_mail(
        subject=f'ABoard - BEST MMORPG Looking for Help Hub: новый отклик на объявление!',
        message=f'Доброго дня, {comment.post.author}, ! На ваше объявление есть новый отклик!\n'
                f'Прочитать отклик:\nhttp://127.0.0.1:8000/comments/{comment.post.id}',
        from_email='aboard.vesoff@outlook.com',
        recipient_list=[comment.post.author.email, ],
    )


@shared_task
def comment_accept_send_email(comment_id):
    comment = Comment.objects.get(id=comment_id)
    print(comment.author.email)
    send_mail(
        subject=f'ABoard - BEST MMORPG Looking for Help Hub: Ваш отклик принят!',
        message=f'Доброго дня, {comment.author}, Автор объявления {comment.post.title} принял Ваш отклик!\n'
                f'Посмотреть принятые отклики:\nhttp://127.0.0.1:8000/comments',
        from_email='aboard.vesoff@outlook.com',
        recipient_list=[comment.author.email, ],
    )
