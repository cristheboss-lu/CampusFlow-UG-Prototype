from django.urls import path
from django.contrib.auth import views as auth_views
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

    # ===== RECUPERACIÓN DE CONTRASEÑA =====
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='plataforma/password_reset.html',
            email_template_name='plataforma/password_reset_email.html',
            subject_template_name='plataforma/password_reset_subject.txt',
            success_url='/password_reset/done/',
        ),
        name='password_reset',
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='plataforma/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='plataforma/password_reset_confirm.html',
            success_url='/reset/done/',
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='plataforma/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
]
