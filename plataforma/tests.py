from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    ActividadPlanificada, Calificacion, Carrera, Certificado, EntregaTarea, Materia,
    Matricula, PerfilDocente, PerfilEstudiante, PerfilUsuario, Periodo,
    Planificacion, Parcial, Tarea, Unidad,
)


def _coma(valor):
    """Formatea un número como lo hace floatformat con LANGUAGE_CODE='es-es' (coma decimal)."""
    return ('%.2f' % valor).replace('.', ',')


class DocenteCalificarParcialTests(TestCase):
    """Regresión para la vista que calcula y guarda la nota de un parcial por pesos."""

    def setUp(self):
        self.carrera = Carrera.objects.create(nombre='Prueba', codigo='PRB')
        self.periodo = Periodo.objects.create(
            nombre='2026-2', fecha_inicio=date(2026, 9, 1), fecha_fin=date(2027, 1, 31), activo=True
        )
        self.user_docente = User.objects.create_user(
            'tc_doc', 'tc_doc@x.com', 'x', first_name='Rosa', last_name='Vera'
        )
        PerfilUsuario.objects.create(user=self.user_docente, rol='docente')
        self.docente = PerfilDocente.objects.create(user=self.user_docente, carrera=self.carrera, cedula='4440001')
        self.materia = Materia.objects.create(
            nombre='Algebra', codigo='ALG-501', carrera=self.carrera, docente=self.docente
        )

        self.planificacion = Planificacion.objects.create(
            materia=self.materia, periodo=self.periodo, docente=self.docente
        )
        self.parcial = Parcial.objects.create(
            planificacion=self.planificacion, numero=1, nombre='Parcial 1',
            peso_formativa=30, peso_practica=30, peso_examen=40,
        )
        unidad = Unidad.objects.create(parcial=self.parcial, numero=1, tema='T')
        act_formativa = ActividadPlanificada.objects.create(
            unidad=unidad, semana=1, nombre='Foro', categoria='formativa', fecha_entrega=date(2026, 9, 10)
        )
        act_practica = ActividadPlanificada.objects.create(
            unidad=unidad, semana=2, nombre='Taller', categoria='practica', fecha_entrega=date(2026, 9, 15)
        )
        act_examen = ActividadPlanificada.objects.create(
            unidad=unidad, semana=3, nombre='Examen', categoria='examen', fecha_entrega=date(2026, 9, 20)
        )

        tarea_f1 = self._crear_tarea(act_formativa, 'F1')
        tarea_f2 = self._crear_tarea(act_formativa, 'F2')
        tarea_p = self._crear_tarea(act_practica, 'P1')
        tarea_e = self._crear_tarea(act_examen, 'E1')
        tarea_suelta = Tarea.objects.create(
            materia=self.materia, titulo='Suelta', descripcion='', fecha_entrega=date(2026, 9, 22)
        )

        self.ana = self._crear_estudiante('tc_a', 'Ana', 'Aranda', '4440101', 'M-201')
        self.matricula_ana = Matricula.objects.create(estudiante=self.ana, periodo=self.periodo, materia=self.materia)
        EntregaTarea.objects.create(tarea=tarea_f1, estudiante=self.ana, calificacion=80)
        EntregaTarea.objects.create(tarea=tarea_f2, estudiante=self.ana, calificacion=90)
        EntregaTarea.objects.create(tarea=tarea_p, estudiante=self.ana, calificacion=90)
        EntregaTarea.objects.create(tarea=tarea_e, estudiante=self.ana, calificacion=78)
        # No pertenece a ningún parcial: no debe influir en el cálculo.
        EntregaTarea.objects.create(tarea=tarea_suelta, estudiante=self.ana, calificacion=100)

        self.beto = self._crear_estudiante('tc_b', 'Beto', 'Bravo', '4440102', 'M-202')
        self.matricula_beto = Matricula.objects.create(estudiante=self.beto, periodo=self.periodo, materia=self.materia)
        EntregaTarea.objects.create(tarea=tarea_f1, estudiante=self.beto, calificacion=70)
        EntregaTarea.objects.create(tarea=tarea_p, estudiante=self.beto, calificacion=60)
        EntregaTarea.objects.create(tarea=tarea_e, estudiante=self.beto)  # entregada sin calificar

        self.url = reverse('docente_calificar_parcial', args=[self.materia.id, self.parcial.id])
        self.client.force_login(self.user_docente)

    def _crear_tarea(self, actividad, titulo):
        return Tarea.objects.create(
            materia=self.materia, actividad=actividad, titulo=titulo, descripcion='',
            fecha_entrega=date(2026, 9, 20),
        )

    def _crear_estudiante(self, username, first_name, last_name, cedula, numero_matricula):
        user = User.objects.create_user(username, f'{username}@x.com', 'x', first_name=first_name, last_name=last_name)
        PerfilUsuario.objects.create(user=user, rol='estudiante')
        PerfilEstudiante.objects.create(
            user=user, carrera=self.carrera, cedula=cedula, numero_matricula=numero_matricula
        )
        return user

    def test_get_calcula_notas_y_marca_incompletas(self):
        response = self.client.get(self.url)
        html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        nota_ana = 85 * 0.30 + 90 * 0.30 + 78 * 0.40  # 83.70
        nota_beto = 70 * 0.30 + 60 * 0.30 + 0 * 0.40  # 39.00
        self.assertIn(_coma(nota_ana), html)
        self.assertIn(_coma(nota_beto), html)
        self.assertIn('Falta examen', html)
        self.assertNotIn(_coma(100), html)  # la tarea suelta no debe aparecer

    def test_guardar_solo_completas(self):
        self.client.post(self.url, {'solo_completas': '1'})

        self.assertEqual(Calificacion.objects.filter(matricula__materia=self.materia).count(), 1)
        calificacion_ana = Calificacion.objects.get(matricula=self.matricula_ana, tipo='Parcial 1')
        self.matricula_ana.refresh_from_db()
        self.assertAlmostEqual(calificacion_ana.valor, 83.70, places=2)
        self.assertAlmostEqual(self.matricula_ana.nota_final, 83.70, places=2)

    def test_guardar_todas_no_duplica(self):
        self.client.post(self.url, {'solo_completas': '1'})
        self.client.post(self.url, {})

        self.matricula_beto.refresh_from_db()
        calificacion_beto = Calificacion.objects.get(matricula=self.matricula_beto, tipo='Parcial 1')
        self.assertAlmostEqual(calificacion_beto.valor, 39.00, places=2)
        self.assertAlmostEqual(self.matricula_beto.nota_final, 39.00, places=2)
        self.assertEqual(
            Calificacion.objects.filter(matricula=self.matricula_ana, tipo='Parcial 1').count(), 1
        )

    def test_nota_final_promedia_varios_parciales(self):
        self.client.post(self.url, {})

        parcial2 = Parcial.objects.create(
            planificacion=self.planificacion, numero=2, nombre='Parcial 2',
            peso_formativa=0, peso_practica=0, peso_examen=100,
        )
        unidad2 = Unidad.objects.create(parcial=parcial2, numero=1, tema='T2')
        act_examen2 = ActividadPlanificada.objects.create(
            unidad=unidad2, semana=8, nombre='Examen 2', categoria='examen', fecha_entrega=date(2026, 10, 20)
        )
        tarea_e2 = self._crear_tarea(act_examen2, 'E2')
        EntregaTarea.objects.create(tarea=tarea_e2, estudiante=self.ana, calificacion=60)

        url_parcial2 = reverse('docente_calificar_parcial', args=[self.materia.id, parcial2.id])
        self.client.post(url_parcial2, {})

        self.matricula_ana.refresh_from_db()
        esperado = round((83.70 + 60) / 2, 2)
        self.assertAlmostEqual(self.matricula_ana.nota_final, esperado, places=2)

    def test_parcial_de_otra_materia_no_es_accesible(self):
        otra_materia = Materia.objects.create(nombre='X', codigo='XXX-1', carrera=self.carrera, docente=self.docente)
        url_otra = reverse('docente_calificar_parcial', args=[otra_materia.id, self.parcial.id])

        response = self.client.get(url_otra)
        self.assertEqual(response.status_code, 302)


class DocenteMateriaPlanificacionTests(TestCase):
    """Regresión para la vista que lista los parciales de una materia y enlaza a calificarlos."""

    def setUp(self):
        self.carrera = Carrera.objects.create(nombre='Prueba', codigo='PRB')
        self.periodo = Periodo.objects.create(
            nombre='2026-2', fecha_inicio=date(2026, 9, 1), fecha_fin=date(2027, 1, 31), activo=True
        )
        self.user_docente = User.objects.create_user(
            'tp_doc', 'tp_doc@x.com', 'x', first_name='Rosa', last_name='Vera'
        )
        PerfilUsuario.objects.create(user=self.user_docente, rol='docente')
        self.docente = PerfilDocente.objects.create(user=self.user_docente, carrera=self.carrera, cedula='4440003')
        self.materia = Materia.objects.create(
            nombre='Algebra', codigo='ALG-502', carrera=self.carrera, docente=self.docente
        )
        self.client.force_login(self.user_docente)
        self.url = reverse('docente_materia_planificacion', args=[self.materia.id])

    def test_sin_periodo_activo_muestra_estado_vacio(self):
        self.periodo.activo = False
        self.periodo.save(update_fields=['activo'])

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No hay un período activo')

    def test_sin_planificacion_la_genera_automaticamente(self):
        self.assertFalse(Planificacion.objects.filter(materia=self.materia, periodo=self.periodo).exists())

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        planificacion = Planificacion.objects.get(materia=self.materia, periodo=self.periodo)

        parciales = list(planificacion.parciales.order_by('numero'))
        self.assertEqual(len(parciales), 3)
        for parcial in parciales:
            self.assertEqual((parcial.peso_formativa, parcial.peso_practica, parcial.peso_examen), (30, 30, 40))

        semanas_por_parcial = [
            list(ActividadPlanificada.objects.filter(unidad__parcial=parcial).order_by('semana').values_list('semana', flat=True))
            for parcial in parciales
        ]
        self.assertEqual(semanas_por_parcial, [list(range(1, 6)), list(range(6, 11)), list(range(11, 17))])

        # La última semana de cada parcial es examen; el resto, formativa.
        for parcial, semanas in zip(parciales, semanas_por_parcial):
            categorias = {
                a.semana: a.categoria
                for a in ActividadPlanificada.objects.filter(unidad__parcial=parcial)
            }
            self.assertEqual(categorias[semanas[-1]], 'examen')
            for semana in semanas[:-1]:
                self.assertEqual(categorias[semana], 'formativa')

        primera_actividad = ActividadPlanificada.objects.get(unidad__parcial=parciales[0], semana=1)
        self.assertEqual(primera_actividad.fecha_entrega, self.periodo.fecha_inicio + timedelta(days=7))
        self.assertFalse(primera_actividad.archivo)

        # Una segunda visita no debe duplicar la planificación.
        self.client.get(self.url)
        self.assertEqual(Planificacion.objects.filter(materia=self.materia, periodo=self.periodo).count(), 1)

    def test_lista_parciales_con_enlace_a_calificar(self):
        planificacion = Planificacion.objects.create(
            materia=self.materia, periodo=self.periodo, docente=self.docente
        )
        parcial = Parcial.objects.create(
            planificacion=planificacion, numero=1, nombre='Parcial 1',
            peso_formativa=30, peso_practica=30, peso_examen=40,
        )
        unidad = Unidad.objects.create(parcial=parcial, numero=1, tema='T')
        ActividadPlanificada.objects.create(
            unidad=unidad, semana=1, nombre='Foro', categoria='formativa', fecha_entrega=date(2026, 9, 10)
        )
        ActividadPlanificada.objects.create(
            unidad=unidad, semana=2, nombre='Taller', categoria='practica', fecha_entrega=date(2026, 9, 15)
        )

        response = self.client.get(self.url)
        html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('Parcial 1', html)
        self.assertIn(reverse('docente_calificar_parcial', args=[self.materia.id, parcial.id]), html)

    def test_materia_ajena_no_es_accesible(self):
        otra_materia = Materia.objects.create(nombre='X', codigo='XXX-2', carrera=self.carrera, docente=None)
        url_otra = reverse('docente_materia_planificacion', args=[otra_materia.id])

        response = self.client.get(url_otra)
        self.assertEqual(response.status_code, 302)


class DocenteActividadEditarTests(TestCase):
    """Regresión para la edición de una actividad planificada (llenar el esqueleto con contenido real)."""

    def setUp(self):
        self.carrera = Carrera.objects.create(nombre='Prueba', codigo='PRB')
        self.periodo = Periodo.objects.create(
            nombre='2026-2', fecha_inicio=date(2026, 9, 1), fecha_fin=date(2027, 1, 31), activo=True
        )
        self.user_docente = User.objects.create_user(
            'ta_doc', 'ta_doc@x.com', 'x', first_name='Rosa', last_name='Vera'
        )
        PerfilUsuario.objects.create(user=self.user_docente, rol='docente')
        self.docente = PerfilDocente.objects.create(user=self.user_docente, carrera=self.carrera, cedula='4440004')
        self.materia = Materia.objects.create(
            nombre='Algebra', codigo='ALG-503', carrera=self.carrera, docente=self.docente
        )
        self.planificacion = Planificacion.objects.create(
            materia=self.materia, periodo=self.periodo, docente=self.docente
        )
        self.parcial = Parcial.objects.create(planificacion=self.planificacion, numero=1, nombre='Parcial 1')
        self.unidad = Unidad.objects.create(parcial=self.parcial, numero=1, tema='Semanas 1-5')
        self.actividad = ActividadPlanificada.objects.create(
            unidad=self.unidad, semana=1, nombre='Semana 1 - Actividad',
            categoria='formativa', fecha_entrega=date(2026, 9, 8),
        )
        self.client.force_login(self.user_docente)
        self.url = reverse('docente_actividad_editar', args=[self.actividad.id])

    def test_edita_nombre_categoria_y_fecha(self):
        response = self.client.post(self.url, {
            'nombre': 'Foro de introducción',
            'categoria': 'practica',
            'fecha_entrega': '2026-09-12',
            'penalizacion_tardia': '0',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.actividad.refresh_from_db()
        self.assertEqual(self.actividad.nombre, 'Foro de introducción')
        self.assertEqual(self.actividad.categoria, 'practica')
        self.assertEqual(self.actividad.fecha_entrega, date(2026, 9, 12))
        self.assertFalse(self.actividad.permite_entrega_tardia)
        self.assertIsNone(self.actividad.fecha_limite_tardia)

    def test_entrega_tardia_requiere_fecha_limite_posterior(self):
        response = self.client.post(self.url, {
            'nombre': 'Foro',
            'categoria': 'formativa',
            'fecha_entrega': '2026-09-12',
            'permite_entrega_tardia': '1',
            'fecha_limite_tardia': '2026-09-10',  # anterior a fecha_entrega: invalido
            'penalizacion_tardia': '10',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.actividad.refresh_from_db()
        # No debe haberse guardado nada: sigue con los valores originales.
        self.assertEqual(self.actividad.nombre, 'Semana 1 - Actividad')
        self.assertFalse(self.actividad.permite_entrega_tardia)

    def test_entrega_tardia_valida_se_guarda(self):
        response = self.client.post(self.url, {
            'nombre': 'Foro',
            'categoria': 'formativa',
            'fecha_entrega': '2026-09-12',
            'permite_entrega_tardia': '1',
            'fecha_limite_tardia': '2026-09-15',
            'penalizacion_tardia': '10',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.actividad.refresh_from_db()
        self.assertTrue(self.actividad.permite_entrega_tardia)
        self.assertEqual(self.actividad.fecha_limite_tardia, date(2026, 9, 15))
        self.assertEqual(self.actividad.penalizacion_tardia, 10)

    def test_actividad_de_otro_docente_no_es_editable(self):
        otro_docente_user = User.objects.create_user('ta_doc2', 'ta_doc2@x.com', 'x')
        PerfilUsuario.objects.create(user=otro_docente_user, rol='docente')
        otro_docente = PerfilDocente.objects.create(user=otro_docente_user, carrera=self.carrera, cedula='4440005')
        self.client.force_login(otro_docente_user)

        response = self.client.post(self.url, {
            'nombre': 'Hackeo',
            'categoria': 'formativa',
            'fecha_entrega': '2026-09-12',
        })

        self.assertEqual(response.status_code, 302)
        self.actividad.refresh_from_db()
        self.assertEqual(self.actividad.nombre, 'Semana 1 - Actividad')


class DashboardEstudianteTests(TestCase):
    """Regresión para el panel del estudiante: % completado, próximas entregas, racha y próximo examen."""

    def setUp(self):
        self.hoy = timezone.now().date()
        self.carrera = Carrera.objects.create(nombre='Prueba', codigo='PRB')
        self.periodo = Periodo.objects.create(
            nombre='2026-2', fecha_inicio=self.hoy - timedelta(days=30),
            fecha_fin=self.hoy + timedelta(days=120), activo=True,
        )
        self.user = User.objects.create_user(
            'te_est', 'te_est@x.com', 'x', first_name='Tere', last_name='Estrada'
        )
        PerfilUsuario.objects.create(user=self.user, rol='estudiante')
        PerfilEstudiante.objects.create(user=self.user, carrera=self.carrera, cedula='7770001', numero_matricula='M-701')

        docente_user = User.objects.create_user('te_doc', 'te_doc@x.com', 'x')
        PerfilUsuario.objects.create(user=docente_user, rol='docente')
        docente = PerfilDocente.objects.create(user=docente_user, carrera=self.carrera, cedula='7770002')

        self.materia = Materia.objects.create(nombre='Fisica', codigo='FIS-1', carrera=self.carrera, docente=docente)
        Matricula.objects.create(estudiante=self.user, materia=self.materia, periodo=self.periodo)

        planificacion = Planificacion.objects.create(materia=self.materia, periodo=self.periodo, docente=docente)
        parcial = Parcial.objects.create(planificacion=planificacion, numero=1, nombre='Parcial 1')
        unidad = Unidad.objects.create(parcial=parcial, numero=1, tema='T')
        self.examen = ActividadPlanificada.objects.create(
            unidad=unidad, semana=5, nombre='Examen 1', categoria='examen',
            fecha_entrega=self.hoy + timedelta(days=10),
        )

        # Ya entregada, a tiempo (completada): due hoy-5, entregada hoy-6.
        self.tarea_completada = Tarea.objects.create(
            materia=self.materia, titulo='T1 Completada', descripcion='',
            fecha_entrega=self.hoy - timedelta(days=5),
        )
        entrega = EntregaTarea.objects.create(
            tarea=self.tarea_completada, estudiante=self.user, estado='Entregado'
        )
        # auto_now_add fija fecha_entrega al crear; la reescribimos para simular
        # que se entregó antes del vencimiento.
        EntregaTarea.objects.filter(id=entrega.id).update(
            fecha_entrega=timezone.now() - timedelta(days=6)
        )

        # Pendiente, ya vencida (atrasada).
        self.tarea_atrasada = Tarea.objects.create(
            materia=self.materia, titulo='T2 Atrasada', descripcion='',
            fecha_entrega=self.hoy - timedelta(days=1),
        )

        # Pendiente, todavía no vence.
        self.tarea_futura = Tarea.objects.create(
            materia=self.materia, titulo='T3 Futura', descripcion='',
            fecha_entrega=self.hoy + timedelta(days=3),
        )

        self.client.force_login(self.user)
        self.url = reverse('dashboard_estudiante')

    def test_stats_y_porcentaje_completado(self):
        response = self.client.get(self.url)
        html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('33%', html)  # 1 de 3 tareas completadas
        self.assertNotIn('T1 Completada', html)  # ya entregada: no en próximas entregas

    def test_proximas_entregas_marca_atrasada_y_pendiente(self):
        response = self.client.get(self.url)
        html = response.content.decode()

        self.assertIn('T2 Atrasada', html)
        self.assertIn('T3 Futura', html)
        idx_atrasada = html.index('T2 Atrasada')
        idx_futura = html.index('T3 Futura')
        self.assertIn('Atrasada', html[idx_atrasada:idx_atrasada + 400])
        self.assertIn('Pendiente', html[idx_futura:idx_futura + 400])

    def test_racha_a_tiempo(self):
        response = self.client.get(self.url)
        html = response.content.decode()

        self.assertIn('1 entrega seguida a tiempo', html)

    def test_proximo_examen_destacado(self):
        response = self.client.get(self.url)
        html = response.content.decode()

        self.assertIn('Examen 1', html)
        self.assertIn('FIS-1', html)

    def test_sin_matriculas_muestra_estado_vacio(self):
        Matricula.objects.filter(estudiante=self.user).delete()

        response = self.client.get(self.url)
        html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Todavía no tienes cursos matriculados')
        self.assertIn('0%', html)


class PortalEstudiantilTests(TestCase):
    """Regresión para el portal administrativo del estudiante: Kardex, datos, matrícula y certificados."""

    def setUp(self):
        self.carrera = Carrera.objects.create(nombre='Prueba', codigo='PRB')
        self.periodo_activo = Periodo.objects.create(
            nombre='2026-2', fecha_inicio=date(2026, 9, 1), fecha_fin=date(2027, 1, 31), activo=True
        )
        self.periodo_pasado = Periodo.objects.create(
            nombre='2026-1', fecha_inicio=date(2026, 1, 1), fecha_fin=date(2026, 6, 30), activo=False
        )
        self.user = User.objects.create_user(
            'pe_est', 'pe_est@x.com', 'x', first_name='Paola', last_name='Espinoza'
        )
        PerfilUsuario.objects.create(user=self.user, rol='estudiante')
        self.perfil = PerfilEstudiante.objects.create(
            user=self.user, carrera=self.carrera, cedula='5550001', numero_matricula='M-501'
        )

        docente_user = User.objects.create_user('pe_doc', 'pe_doc@x.com', 'x')
        PerfilUsuario.objects.create(user=docente_user, rol='docente')
        docente = PerfilDocente.objects.create(user=docente_user, carrera=self.carrera, cedula='5550002')

        self.materia_actual = Materia.objects.create(
            nombre='Quimica', codigo='QUI-1', carrera=self.carrera, docente=docente, creditos=5
        )
        self.materia_pasada = Materia.objects.create(
            nombre='Fisica', codigo='FIS-1', carrera=self.carrera, docente=docente, creditos=3
        )

        self.matricula_actual = Matricula.objects.create(
            estudiante=self.user, materia=self.materia_actual, periodo=self.periodo_activo, estado='Cursando'
        )
        self.matricula_pasada = Matricula.objects.create(
            estudiante=self.user, materia=self.materia_pasada, periodo=self.periodo_pasado,
            estado='Aprobado', nota_final=88,
        )

        self.client.force_login(self.user)
        self.url = reverse('portal_estudiantil')

    def test_kardex_incluye_todas_las_materias_sin_filtrar_por_periodo(self):
        response = self.client.get(self.url)
        html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('QUI-1', html)
        self.assertIn('FIS-1', html)  # del período pasado: el Kardex es historial completo

    def test_promedio_y_creditos_usan_solo_notas_no_nulas(self):
        response = self.client.get(self.url)
        html = response.content.decode()

        # Solo la matricula pasada tiene nota_final (88); la actual es None.
        # floatformat usa coma decimal por LANGUAGE_CODE='es-es'.
        self.assertIn('88,0', html)
        # 5 + 3 = 8 créditos cursados en total.
        self.assertIn('8', html)

    def test_datos_personales_de_solo_lectura(self):
        response = self.client.get(self.url)
        self.assertContains(response, '5550001')  # cedula
        self.assertContains(response, 'M-501')    # numero_matricula
        self.assertContains(response, 'Prueba')   # carrera

    def test_estado_matricula_solo_periodo_activo(self):
        response = self.client.get(self.url)
        html = response.content.decode()

        self.assertIn('QUI-1', html)
        # FIS-1 sigue apareciendo en el Kardex, pero no debe listarse dos veces
        # en la sección de "Estado de matrícula" del período activo.
        idx_estado_matricula = html.index('Estado de matrícula')
        self.assertNotIn('FIS-1', html[idx_estado_matricula:])

    def test_solicitar_certificado_crea_pendiente_sin_fecha(self):
        response = self.client.post(self.url, {'tipo': 'notas'}, follow=True)

        self.assertEqual(response.status_code, 200)
        certificado = Certificado.objects.get(estudiante=self.user)
        self.assertEqual(certificado.tipo, 'notas')
        self.assertEqual(certificado.estado, 'Pendiente')
        self.assertIsNone(certificado.fecha_emision)
        self.assertEqual(certificado.carrera, self.perfil.carrera)

    def test_tipo_invalido_no_crea_certificado(self):
        response = self.client.post(self.url, {'tipo': 'algo_raro'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Certificado.objects.filter(estudiante=self.user).exists())

    def test_sin_perfil_estudiante_redirige(self):
        user_sin_perfil = User.objects.create_user('sin_perfil', 'sp@x.com', 'x')
        PerfilUsuario.objects.create(user=user_sin_perfil, rol='estudiante')
        self.client.force_login(user_sin_perfil)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class SecretariaCertificadosProcesarTests(TestCase):
    """Regresión para aprobar/rechazar solicitudes de certificado pendientes."""

    def setUp(self):
        self.carrera = Carrera.objects.create(nombre='Prueba', codigo='PRB')
        self.admin_user = User.objects.create_user('sc_admin', 'sc_admin@x.com', 'x')
        PerfilUsuario.objects.create(user=self.admin_user, rol='admin')

        self.estudiante = User.objects.create_user('sc_est', 'sc_est@x.com', 'x', first_name='Luis', last_name='Vera')
        PerfilUsuario.objects.create(user=self.estudiante, rol='estudiante')
        PerfilEstudiante.objects.create(user=self.estudiante, carrera=self.carrera, cedula='6660001', numero_matricula='M-601')

        self.certificado = Certificado.objects.create(
            estudiante=self.estudiante, carrera=self.carrera, tipo='matricula',
            estado='Pendiente', codigo_verificacion='TEST-0001',
        )
        self.client.force_login(self.admin_user)
        self.url = reverse('secretaria_certificados_procesar', args=[self.certificado.id])

    def test_aprobar_emite_y_fija_fecha(self):
        response = self.client.post(self.url, {'accion': 'aprobar'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.certificado.refresh_from_db()
        self.assertEqual(self.certificado.estado, 'Emitido')
        self.assertIsNotNone(self.certificado.fecha_emision)

    def test_rechazar_no_fija_fecha(self):
        response = self.client.post(self.url, {'accion': 'rechazar'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.certificado.refresh_from_db()
        self.assertEqual(self.certificado.estado, 'Rechazado')
        self.assertIsNone(self.certificado.fecha_emision)

    def test_filtro_por_estado_pendiente(self):
        Certificado.objects.create(
            estudiante=self.estudiante, carrera=self.carrera, tipo='notas',
            estado='Emitido', fecha_emision=date(2026, 9, 1), codigo_verificacion='TEST-0002',
        )

        response = self.client.get(reverse('secretaria_certificados'), {'estado': 'Pendiente'})
        html = response.content.decode()

        # El código de trámite solo aparece en filas reales de la tabla, nunca
        # en el modal estático de "Generar certificado" (que sí lista los 3
        # tipos siempre) — es un chequeo inequívoco de qué filas se muestran.
        self.assertIn('TEST-0001', html)
        self.assertNotIn('TEST-0002', html)


class LoginNextTests(TestCase):
    """Regresión: login_estudiante debe respetar ?next= (validado) en vez de siempre usar el rol."""

    def setUp(self):
        self.carrera = Carrera.objects.create(nombre='Prueba', codigo='PRB')
        self.user = User.objects.create_user('ln_est', 'ln_est@x.com', 'x')
        PerfilUsuario.objects.create(user=self.user, rol='estudiante')
        PerfilEstudiante.objects.create(user=self.user, carrera=self.carrera, cedula='9990001', numero_matricula='M-901')

    def test_get_sin_login_redirige_con_next(self):
        response = self.client.get('/portal-estudiantil/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/?next=/portal-estudiantil/')

    def test_login_get_incluye_next_en_campo_oculto(self):
        response = self.client.get(reverse('login'), {'next': '/portal-estudiantil/'})

        self.assertContains(response, 'name="next" value="/portal-estudiantil/"')

    def test_login_post_respeta_next_valido(self):
        response = self.client.post(reverse('login'), {
            'username': 'ln_est', 'password': 'x', 'next': '/portal-estudiantil/',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/portal-estudiantil/')

    def test_login_post_rechaza_next_externo(self):
        response = self.client.post(reverse('login'), {
            'username': 'ln_est', 'password': 'x', 'next': 'https://evil.com/robar',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard_estudiante'))

    def test_login_post_sin_next_usa_rol(self):
        response = self.client.post(reverse('login'), {'username': 'ln_est', 'password': 'x'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard_estudiante'))


class BackfillPerfilUsuarioMigrationTests(TestCase):
    """
    Regresión para la migración 0011: crea el PerfilUsuario que le falte a
    cualquier PerfilEstudiante/PerfilDocente, sin duplicar a quien ya lo tiene.
    """

    def setUp(self):
        self.carrera = Carrera.objects.create(nombre='Prueba', codigo='PRB')

    def _correr_backfill(self):
        import importlib
        from django.apps import apps
        # El nombre del módulo empieza con un dígito: no es un identificador
        # Python válido para "import" normal, se carga por ruta con importlib.
        modulo = importlib.import_module(
            'plataforma.migrations.0011_backfill_perfilusuario_faltantes'
        )
        modulo.backfill_perfilusuario(apps, None)

    def test_crea_perfilusuario_faltante_de_estudiante(self):
        user = User.objects.create_user('bf_est', 'bf_est@x.com', 'x')
        PerfilEstudiante.objects.create(user=user, carrera=self.carrera, cedula='8880001', numero_matricula='M-801')
        self.assertFalse(PerfilUsuario.objects.filter(user=user).exists())

        self._correr_backfill()

        perfil = PerfilUsuario.objects.get(user=user)
        self.assertEqual(perfil.rol, 'estudiante')

    def test_crea_perfilusuario_faltante_de_docente(self):
        user = User.objects.create_user('bf_doc', 'bf_doc@x.com', 'x')
        PerfilDocente.objects.create(user=user, carrera=self.carrera, cedula='8880002')
        self.assertFalse(PerfilUsuario.objects.filter(user=user).exists())

        self._correr_backfill()

        perfil = PerfilUsuario.objects.get(user=user)
        self.assertEqual(perfil.rol, 'docente')

    def test_no_duplica_a_quien_ya_tiene_perfilusuario(self):
        user = User.objects.create_user('bf_est2', 'bf_est2@x.com', 'x')
        PerfilEstudiante.objects.create(user=user, carrera=self.carrera, cedula='8880003', numero_matricula='M-802')
        PerfilUsuario.objects.create(user=user, rol='estudiante')

        self._correr_backfill()

        self.assertEqual(PerfilUsuario.objects.filter(user=user).count(), 1)

    def test_no_toca_usuarios_sin_perfil_especifico(self):
        # Un superusuario sin PerfilEstudiante/PerfilDocente (como 'admin' en
        # producción) no debe recibir un PerfilUsuario por el backfill.
        admin_user = User.objects.create_user('bf_admin', 'bf_admin@x.com', 'x', is_staff=True, is_superuser=True)

        self._correr_backfill()

        self.assertFalse(PerfilUsuario.objects.filter(user=admin_user).exists())
