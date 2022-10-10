from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)
        labels = {
            'text': 'Напишите свой пост ниже',
            'group': 'Группа',
            'image': 'Картинка',
        }

    def clean(self):
        super(PostForm, self).clean()
        text = self.cleaned_data.get('text')
        if text is None or len(text) == 0:
            self._errors['text'] = self.error_class([
                'А кто поле будет заполнять? Пушкин?'
            ])
        return self.cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )

    def clean(self):
        super(CommentForm, self).clean()
        text = self.cleaned_data.get('text')
        if text is None or len(text) == 0:
            self._errors['text'] = self.error_class([
                'А кто поле будет заполнять? Пушкин?'
            ])
        return self.cleaned_data
