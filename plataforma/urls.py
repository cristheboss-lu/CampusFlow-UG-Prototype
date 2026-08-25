from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('portal-estudiantil/', views.portal_estudiantil, name='portal_estudiantil'),
    path('biblioteca/', views.biblioteca, name='biblioteca'),
    path('admisiones/', views.admisiones, name='admisiones'),
    path('contacto/', views.contacto, name='contacto'),
    path('contacto-exito/', views.contacto_exito, name='contacto_exito'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('aulas-virtuales/', views.aulas_virtuales, name='aulas_virtuales'),
    path('mis-cursos/', views.cursos_view, name='cursos'),
]
