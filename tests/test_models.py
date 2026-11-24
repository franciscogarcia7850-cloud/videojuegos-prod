import os
import unittest
from decimal import Decimal

# Antes de importar la app para que use la base de datos de pruebas
os.environ['FLASK_CONFIG'] = 'testing'

from sqlalchemy.exc import IntegrityError

from app import app, db
from models import Juego, User
import controllers


class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_juego_creation(self):
        j = Juego(nombre='Test', descripcion='Desc', precio=9.99)
        db.session.add(j)
        db.session.commit()
        self.assertEqual(Juego.query.count(), 1)

    def test_juego_guarda_sus_datos(self):
        db.session.add(Juego(nombre='Zelda', descripcion='Aventura', precio=59.99))
        db.session.commit()
        juego = Juego.query.first()
        self.assertEqual(juego.nombre, 'Zelda')
        self.assertEqual(juego.descripcion, 'Aventura')
        self.assertEqual(juego.precio, Decimal('59.99'))

    def test_juego_sin_nombre_no_se_guarda(self):
        db.session.add(Juego(descripcion='Sin nombre', precio=10))
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_user_password_se_guarda_como_hash(self):
        u = User(username='fran', password='secreto123')
        self.assertIsNotNone(u.password_hash)
        self.assertNotEqual(u.password_hash, 'secreto123')

    def test_user_verify_password(self):
        u = User(username='fran', password='secreto123')
        self.assertTrue(u.verify_password('secreto123'))
        self.assertFalse(u.verify_password('otra'))

    def test_user_password_no_se_puede_leer(self):
        u = User(username='fran', password='secreto123')
        with self.assertRaises(AttributeError):
            u.password

    def test_user_misma_password_hash_diferente(self):
        u1 = User(username='fran', password='secreto123')
        u2 = User(username='ana', password='secreto123')
        self.assertNotEqual(u1.password_hash, u2.password_hash)

    def test_user_username_unico(self):
        db.session.add(User(username='fran', password='abc123'))
        db.session.commit()
        db.session.add(User(username='fran', password='xyz789'))
        with self.assertRaises(IntegrityError):
            db.session.commit()


class ControllersTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_insertar_y_obtener_juegos(self):
        controllers.insertar_juego('Mario', 'Plataformas', 49.99)
        controllers.insertar_juego('Halo', 'Disparos', 39.99)
        juegos = controllers.obtener_juegos()
        self.assertEqual(len(juegos), 2)
        self.assertEqual([j.nombre for j in juegos], ['Mario', 'Halo'])

    def test_obtener_juego_por_id(self):
        controllers.insertar_juego('Mario', 'Plataformas', 49.99)
        juego = controllers.obtener_juego_por_id(1)
        self.assertEqual(juego.nombre, 'Mario')
        self.assertIsNone(controllers.obtener_juego_por_id(99))

    def test_actualizar_juego(self):
        controllers.insertar_juego('Mario', 'Plataformas', 49.99)
        controllers.actualizar_juego('Mario Kart', 'Carreras', 59.99, 1)
        juego = controllers.obtener_juego_por_id(1)
        self.assertEqual(juego.nombre, 'Mario Kart')
        self.assertEqual(juego.descripcion, 'Carreras')
        self.assertEqual(juego.precio, Decimal('59.99'))

    def test_eliminar_juego(self):
        controllers.insertar_juego('Mario', 'Plataformas', 49.99)
        controllers.eliminar_juego(1)
        self.assertEqual(Juego.query.count(), 0)


if __name__ == '__main__':
    unittest.main()
