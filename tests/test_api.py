import os
import json
import unittest

# Antes de importar la app para que use la base de datos de pruebas
os.environ['FLASK_CONFIG'] = 'testing'

from app import app, db
from models import Juego


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        db.session.add(Juego(nombre='X', descripcion='Y', precio=1.23))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_get_juegos(self):
        resp = self.client.get('/api/juegos')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], {'id': 1, 'nombre': 'X', 'descripcion': 'Y', 'precio': 1.23})

    def test_respuesta_es_json(self):
        resp = self.client.get('/api/juegos')
        self.assertEqual(resp.content_type, 'application/json')

    def test_get_juego_por_id(self):
        resp = self.client.get('/api/juegos/1')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['nombre'], 'X')

    def test_get_juego_inexistente(self):
        resp = self.client.get('/api/juegos/99')
        self.assertEqual(resp.status_code, 404)
        self.assertIn('message', resp.get_json())

    def test_post_juego(self):
        resp = self.client.post('/api/juegos', json={'nombre': 'Tetris', 'descripcion': 'Puzzle', 'precio': 5.5})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.get_json()['nombre'], 'Tetris')
        self.assertEqual(Juego.query.count(), 2)

    def test_post_juego_sin_nombre(self):
        resp = self.client.post('/api/juegos', json={'descripcion': 'Puzzle', 'precio': 5.5})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Juego.query.count(), 1)

    def test_post_juego_precio_invalido(self):
        resp = self.client.post('/api/juegos', json={'nombre': 'Tetris', 'descripcion': 'Puzzle', 'precio': 'abc'})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Juego.query.count(), 1)

    def test_put_juego(self):
        resp = self.client.put('/api/juegos/1', json={'nombre': 'X2', 'descripcion': 'Y2', 'precio': 2.5})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['nombre'], 'X2')
        self.assertEqual(db.session.get(Juego, 1).descripcion, 'Y2')

    def test_put_juego_inexistente(self):
        resp = self.client.put('/api/juegos/99', json={'nombre': 'X2', 'descripcion': 'Y2', 'precio': 2.5})
        self.assertEqual(resp.status_code, 404)

    def test_delete_juego(self):
        resp = self.client.delete('/api/juegos/1')
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(Juego.query.count(), 0)

    def test_delete_juego_inexistente(self):
        resp = self.client.delete('/api/juegos/99')
        self.assertEqual(resp.status_code, 404)


if __name__ == '__main__':
    unittest.main()
