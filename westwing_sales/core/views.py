# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from westwing_sales.core.get_products import get_all_products

__author__ = 'mateuszdargacz@gmail.com'
__date__ = '3/12/16 / 2:59 PM'
__git__ = 'https://github.com/mateuszdargacz'



class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'core/home.html'

    def get(self, request, *args, **kwargs):
        context = dict()
        context.update(campaigns=get_all_products())

        return self.render_to_response(context)
