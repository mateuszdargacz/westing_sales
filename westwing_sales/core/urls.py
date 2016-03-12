# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from westwing_sales.core import views

__author__ = 'mateuszdargacz@gmail.com'
__date__ = '3/8/16 / 2:10 PM'
__git__ = 'https://github.com/mateuszdargacz'


urlpatterns = [
    # URL pattern for the UserListView
    url(
        regex=r'^$',
        view=views.HomeView.as_view(),
        name='home'
    ),

]
