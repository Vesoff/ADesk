from django_filters import FilterSet, DateFilter
from .models import Post
from django import forms


class PostFilter(FilterSet):
    date = DateFilter(field_name='time_in', widget=forms.DateInput(attrs={'type': 'date'}), label='Поиск по дате',
                      lookup_expr='date__gte')

    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
        }


class CommentsFilterForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(CommentsFilterForm, self).__init__(*args, **kwargs)
        self.fields['title'] = forms.ModelChoiceField(
            label='Объявление',
            queryset=Post.objects.filter(author_id=user.id).order_by('-time_in').values_list('title', flat=True),
            empty_label="Все",
            required=False
        )
