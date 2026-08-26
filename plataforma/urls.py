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
    path('importar-estudiantes/', views.importar_estudiantes, name='importar_estudiantes'),
    path('login/', views.login_estudiante, name='login'),
    path('logout/', views.logout_estudiante, name='logout'),
    path('dashboard/', views.dashboard_estudiante, name='dashboard_estudiante'),
]
