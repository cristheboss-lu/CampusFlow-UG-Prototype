from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ===== VISTAS PÚBLICAS =====
    path('', views.index, name='index'),
    path('aulas-virtuales/', views.aulas_virtuales, name='aulas_virtuales'),
    path('portal-estudiantil/', views.portal_estudiantil, name='portal_estudiantil'),
    path('biblioteca/', views.biblioteca, name='biblioteca'),
    path('admisiones/', views.admisiones, name='admisiones'),
    path('contacto/', views.contacto, name='contacto'),
    path('contacto-exito/', views.contacto_exito, name='contacto_exito'),
    
    # ===== IMPORTACIÓN LEGACY =====
    path('importar-estudiantes/', views.importar_estudiantes, name='importar_estudiantes'),
    
    # ===== AUTENTICACIÓN ESTUDIANTES =====
    path('login/', views.login_estudiante, name='login'),
    path('logout/', views.logout_estudiante, name='logout'),
    path('dashboard/', views.dashboard_estudiante, name='dashboard_estudiante'),
    path('curso/<int:matricula_id>/', views.detalle_curso, name='detalle_curso'),
    path('tarea/<int:tarea_id>/entregar/', views.entregar_tarea, name='entregar_tarea'),

    # ===== PANEL DOCENTE =====
    path('docente/', views.dashboard_docente, name='dashboard_docente'),
    path('docente/materia/<int:materia_id>/tareas/', views.docente_materia_tareas, name='docente_materia_tareas'),
    path('docente/tarea/<int:tarea_id>/entregas/', views.docente_tarea_entregas, name='docente_tarea_entregas'),
    path('docente/materia/<int:materia_id>/estudiantes/', views.docente_materia_estudiantes, name='docente_materia_estudiantes'),
    path('docente/materia/<int:materia_id>/planificacion/', views.docente_materia_planificacion, name='docente_materia_planificacion'),
    path('docente/actividad/<int:actividad_id>/editar/', views.docente_actividad_editar, name='docente_actividad_editar'),
    path('docente/materia/<int:materia_id>/parcial/<int:parcial_id>/calificar/', views.docente_calificar_parcial, name='docente_calificar_parcial'),

    # ===== PANEL SECRETARÍA =====
    path('secretaria/', views.panel_secretaria, name='panel_secretaria'),

    # ===== SECCIÓN: USUARIOS =====
    path('secretaria/usuarios/', views.secretaria_usuarios, name='secretaria_usuarios'),
    path('secretaria/usuarios/carga-masiva/', views.secretaria_carga_masiva, name='secretaria_carga_masiva'),

    # ===== SECCIÓN: CARRERAS =====
    path('secretaria/carreras/', views.secretaria_carreras, name='secretaria_carreras'),
    path('secretaria/carreras/<int:carrera_id>/editar/', views.secretaria_carreras_editar, name='secretaria_carreras_editar'),
    path('secretaria/carreras/<int:carrera_id>/eliminar/', views.secretaria_carreras_eliminar, name='secretaria_carreras_eliminar'),
    path('secretaria/carreras/carga-masiva/', views.secretaria_carreras_carga_masiva, name='secretaria_carreras_carga_masiva'),

    # ===== SECCIÓN: PERÍODOS =====
    path('secretaria/periodos/', views.secretaria_periodos, name='secretaria_periodos'),
    path('secretaria/periodos/<int:periodo_id>/editar/', views.secretaria_periodos_editar, name='secretaria_periodos_editar'),
    path('secretaria/periodos/<int:periodo_id>/eliminar/', views.secretaria_periodos_eliminar, name='secretaria_periodos_eliminar'),
    path('secretaria/periodos/carga-masiva/', views.secretaria_periodos_carga_masiva, name='secretaria_periodos_carga_masiva'),

    # ===== SECCIÓN: MATERIAS =====
    path('secretaria/materias/', views.secretaria_materias, name='secretaria_materias'),
    path('secretaria/materias/<int:materia_id>/editar/', views.secretaria_materias_editar, name='secretaria_materias_editar'),
    path('secretaria/materias/<int:materia_id>/eliminar/', views.secretaria_materias_eliminar, name='secretaria_materias_eliminar'),
    path('secretaria/materias/carga-masiva/', views.secretaria_materias_carga_masiva, name='secretaria_materias_carga_masiva'),

    # ===== SECCIÓN: MATRÍCULAS =====
    path('secretaria/matriculas/', views.secretaria_matriculas, name='secretaria_matriculas'),
    path('secretaria/matriculas/<int:matricula_id>/editar/', views.secretaria_matriculas_editar, name='secretaria_matriculas_editar'),
    path('secretaria/matriculas/<int:matricula_id>/eliminar/', views.secretaria_matriculas_eliminar, name='secretaria_matriculas_eliminar'),
    path('secretaria/matriculas/carga-masiva/', views.secretaria_matriculas_carga_masiva, name='secretaria_matriculas_carga_masiva'),

    # ===== SECCIÓN: CERTIFICADOS =====
    path('secretaria/certificados/', views.secretaria_certificados, name='secretaria_certificados'),
    path('secretaria/certificados/<int:certificado_id>/eliminar/', views.secretaria_certificados_eliminar, name='secretaria_certificados_eliminar'),
    path('secretaria/certificados/carga-masiva/', views.secretaria_certificados_carga_masiva, name='secretaria_certificados_carga_masiva'),
    path('certificados/<int:certificado_id>/descargar/', views.descargar_certificado, name='descargar_certificado'),

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
