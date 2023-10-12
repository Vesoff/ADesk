import random

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import FormView, UpdateView
from .models import UsersAuth
from .forms import EditProfile, AuthcodeForm


code_not_correct = str('')


class AccountProfile(FormView):
    template_name = 'account/profile.html'
    form_class = AuthcodeForm

    def dispatch(self, request, *args, **kwargs):
        if UsersAuth.objects.filter(user=self.request.user).exists():
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('auth_code'))

    def form_valid(self, form, **kwargs):
        global code_not_correct
        if form.cleaned_data['code'] == UsersAuth.objects.get(user=self.request.user).code:
            Group.objects.get(name='Registered').user_set.add(self.request.user)
        else:
            code_not_correct = "Введен неверный код подтверждения"
        return HttpResponseRedirect(reverse('account_profile'))

    def get_context_data(self, **kwargs):
        context = super(AccountProfile, self).get_context_data(**kwargs)
        context['code_not_correct'] = code_not_correct
        if self.request.user.groups.filter(name='Registered').exists():
            context['auth'] = True
        else:
            context['auth'] = False
        return context


@login_required
def auth_code(request):
    global code_not_correct
    code_not_correct = ""

    if not UsersAuth.objects.filter(user=request.user).exists():
        add_user = UsersAuth()
        add_user.user = request.user
        add_user.save()

    user = UsersAuth.objects.get(user=request.user)
    user.code = random.randint(1000, 9999)
    user.save()
    send_mail(
        subject=f'ABoard - BEST MMORPG Looking for Help Hub: подтверждение e-mail',
        message=f'Доброго дня, {request.user}! Для подтверждения регистрации, введите код {user.code} на '
               f'странице регистрации\nhttp://127.0.0.1:8000/accounts/profile',
        from_email='aboard.vesoff@outlook.com',
        recipient_list=[request.user.email, ],
    )
    return HttpResponseRedirect(reverse('account_profile'))


class UpdateProfile(UpdateView):
    model = User
    form_class = EditProfile
    success_url = '/accounts/profile'
    template_name = 'account/update_profile.html'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
          queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)
