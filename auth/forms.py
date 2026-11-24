from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Regexp, EqualTo

from models import User


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(message='Escribe tu usuario')])
    password = PasswordField('Contraseña', validators=[DataRequired(message='Escribe tu contraseña')])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Ingresar')


class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(message='Escribe un usuario'),
        Length(3, 64, message='El usuario debe tener entre 3 y 64 caracteres'),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'El usuario solo puede tener letras, números, puntos o guiones bajos')])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='Escribe una contraseña'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres'),
        EqualTo('password2', message='Las contraseñas no coinciden')])
    password2 = PasswordField('Confirmar contraseña', validators=[DataRequired(message='Confirma tu contraseña')])
    submit = SubmitField('Registrarme')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Ese usuario ya está registrado')
