import os
import unittest

# Antes de importar la app para que use la base de datos de pruebas
os.environ['FLASK_CONFIG'] = 'testing'

from app import app, db
from models import Juego, User


class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        db.session.add(User(username='fran', password='secreto123'))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def login(self, username='fran', password='secreto123'):
        return self.client.post('/auth/login', data={'username': username, 'password': password})

    # Rutas no protegidas

    def test_login_page_access(self):
        resp = self.client.get('/auth/login')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Ingresar', resp.get_data(as_text=True))

    def test_register_page_access(self):
        resp = self.client.get('/auth/register')
        self.assertEqual(resp.status_code, 200)

    def test_pagina_inexistente_404(self):
        resp = self.client.get('/no_existe')
        self.assertEqual(resp.status_code, 404)

    # Rutas protegidas sin sesion

    def test_index_requires_login(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/auth/login', resp.headers['Location'])

    def test_rutas_protegidas_redirigen_al_login(self):
        for ruta in ['/juegos', '/agregar_juego', '/formulario_editar_juego/1', '/videogame/1', '/auth/logout']:
            with self.subTest(ruta=ruta):
                resp = self.client.get(ruta)
                self.assertEqual(resp.status_code, 302)
                self.assertIn('/auth/login', resp.headers['Location'])

    # Autenticacion

    def test_login_correcto(self):
        resp = self.login()
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/juegos', resp.headers['Location'])
        resp = self.client.get('/juegos')
        self.assertEqual(resp.status_code, 200)

    def test_login_incorrecto(self):
        resp = self.login(password='equivocada')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Usuario o contraseña incorrectos', resp.get_data(as_text=True))

    def test_registro_crea_usuario(self):
        resp = self.client.post('/auth/register', data={
            'username': 'ana', 'password': 'clave123', 'password2': 'clave123'})
        self.assertEqual(resp.status_code, 302)
        self.assertIsNotNone(User.query.filter_by(username='ana').first())

    def test_registro_passwords_no_coinciden(self):
        resp = self.client.post('/auth/register', data={
            'username': 'ana', 'password': 'clave123', 'password2': 'otra123'})
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(User.query.filter_by(username='ana').first())

    def test_logout(self):
        self.login()
        resp = self.client.get('/auth/logout')
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get('/juegos')
        self.assertEqual(resp.status_code, 302)

    # Rutas protegidas con sesion

    def test_guardar_juego(self):
        self.login()
        resp = self.client.post('/guardar_juego', data={
            'nombre': 'Minecraft', 'descripcion': 'Construccion', 'precio': '29.99'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Juego.query.count(), 1)
        resp = self.client.get('/juegos')
        self.assertIn('Minecraft', resp.get_data(as_text=True))

    def test_actualizar_juego(self):
        db.session.add(Juego(nombre='Halo', descripcion='Disparos', precio=39.99))
        db.session.commit()
        self.login()
        resp = self.client.post('/actualizar_juego', data={
            'id': '1', 'nombre': 'Halo 2', 'descripcion': 'Disparos', 'precio': '19.99'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(db.session.get(Juego, 1).nombre, 'Halo 2')

    def test_eliminar_juego(self):
        db.session.add(Juego(nombre='Halo', descripcion='Disparos', precio=39.99))
        db.session.commit()
        self.login()
        resp = self.client.post('/eliminar_juego', data={'id': '1'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Juego.query.count(), 0)

    def test_videogame_sin_id_400(self):
        self.login()
        resp = self.client.get('/videogame')
        self.assertEqual(resp.status_code, 400)

    def test_videogame_no_existe_404(self):
        self.login()
        resp = self.client.get('/videogame/99')
        self.assertEqual(resp.status_code, 404)


if __name__ == '__main__':
    unittest.main()
