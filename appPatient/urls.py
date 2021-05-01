from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('/info', views.info, name='Get User Info'),
    path('/visit', views.visit_req, name='Visit'),
    path('/visit/<int:order_id>', views.get_visit_detail, name='Get Visit Details'),
    path('/health', views.health, name='Health Check')
]
