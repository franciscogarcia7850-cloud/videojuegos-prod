U4 - A4 Despliegue de Producción del Mini-Sistema de Videojuegos

App de videojuegos en Flask con login. Corre en Docker con Gunicorn y MySQL.

Pasos para levantar la aplicación

Abrir Docker Desktop, clonar el repositorio, entrar a la carpeta y correr: docker compose up --build -d

Después entrar a http://localhost, registrarse e iniciar sesión.

Variables de entorno

Están en docker-compose.yml. DATABASE_URL es la conexión a MySQL y SECRET_KEY es la clave de las sesiones. MYSQL_ROOT_PASSWORD, MYSQL_DATABASE, MYSQL_USER y MYSQL_PASSWORD son los datos de la base de datos.

Comandos usados

Para levantar la app: docker compose up --build -d

Para ver los contenedores: docker compose ps

Para ver los mensajes de la app: docker compose logs web

Para apagar la app: docker compose down

Capturas de pantalla

Registro

![Registro](capturas/registro.png)

Login

![Login](capturas/login.png)

Agregar juego

![Agregar](capturas/agregar.png)

Editar juego

![Editar](capturas/editar.png)

Lista de juegos

![Lista](capturas/lista.png)
