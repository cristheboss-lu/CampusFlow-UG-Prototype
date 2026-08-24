from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('aulas-virtuales/', views.aulas_virtuales, name='aulas_virtuales'),
    path('portal-estudiantil/', views.portal_estudiantil, name='portal_estudiantil'),
    path('biblioteca/', views.biblioteca, name='biblioteca'),
    path('admisiones/', views.admisiones, name='admisiones'),
    path('contacto/', views.contacto, name='contacto'),
    path('contacto-exito/', views.contacto_exito, name='contacto_exito'),
]
from .views import login_view, logout_view, cursos_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('mis-cursos/', cursos_view, name='cursos'),
]