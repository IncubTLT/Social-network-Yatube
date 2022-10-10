"""Static pages views function."""
from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author_title'] = 'Страница об авторе.'
        context['author_text'] = ('На создание этой страницы '
                                  'у меня ушло пять минут! Ай да я.'
                                  )
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tech_title'] = 'Страница об авторе.'
        context['tech_text'] = ('На создание этой страницы '
                                'у меня ушло пять минут! Ай да я.'
                                )
        return context
