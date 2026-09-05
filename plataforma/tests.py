from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import (
    ActividadPlanificada, Calificacion, Carrera, EntregaTarea, Materia,
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

    def test_sin_planificacion_muestra_estado_vacio(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'no tiene una planificación')

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
