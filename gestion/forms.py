"""ModelForms reales para las 17 entidades, con control explícito de campos sensibles."""
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import modelform_factory

from organizacion.models import PerfilUsuario, Rol

User = get_user_model()


class EstiloCamposMixin:
    """Los widgets ayudan al usuario, pero todas las reglas se validan en Django."""
    def aplicar_estilo(self):
        for campo in self.fields.values():
            widget = campo.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = 'control-check'
            elif isinstance(widget, forms.SelectMultiple):
                widget.attrs['class'] = 'control-form control-multiple'
                widget.attrs['size'] = 5
            else:
                widget.attrs['class'] = 'control-form'
            if isinstance(campo, forms.DateField):
                widget.input_type = 'date'
                widget.format = '%Y-%m-%d'
                if isinstance(widget, forms.DateInput):
                    widget.attrs['type'] = 'date'
        # Django valida las entradas independientemente de atributos HTML.


class ModeloSGRForm(EstiloCamposMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilo()


class RolForm(ModeloSGRForm):
    class Meta:
        model = Rol
        fields = ['codigo', 'nombre', 'descripcion', 'activo']
    # No incluir grupo, permisos, users, is_staff ni is_superuser.


class FuncionarioForm(ModeloSGRForm):
    """Perfil + User de Django, sin exponer campos de privilegios.

    Las contraseñas se procesan exclusivamente con set_password().
    Los grupos/permisos de Django NO cambian desde este formulario.
    """
    username = forms.CharField(label='Usuario para iniciar sesión', max_length=150)
    nombres = forms.CharField(label='Nombres', max_length=150)
    apellidos = forms.CharField(label='Apellidos', max_length=150)
    correo = forms.EmailField(label='Correo electrónico')
    clave = forms.CharField(
        label='Contraseña nueva', required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text='Obligatoria al crear; dejar vacía al editar para conservarla.',
    )
    confirmar_clave = forms.CharField(
        label='Confirmar contraseña', required=False,
        widget=forms.PasswordInput(render_value=False),
    )
    activo_funcionario = forms.BooleanField(label='Usuario activo', required=False, initial=True)

    class Meta:
        model = PerfilUsuario
        fields = ['rol', 'delegacion', 'rut', 'cargo', 'roles']

    def __init__(self, *args, **kwargs):
        self.actor = kwargs.pop('actor', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            u = self.instance.usuario
            self.fields['username'].initial = u.username
            self.fields['nombres'].initial = u.first_name
            self.fields['apellidos'].initial = u.last_name
            self.fields['correo'].initial = u.email
            self.fields['activo_funcionario'].initial = u.is_active

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        existentes = User.objects.filter(username__iexact=username)
        if self.instance and self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.usuario_id)
        if existentes.exists():
            raise ValidationError('Ya existe una cuenta con ese nombre de usuario.')
        return username

    def clean(self):
        datos = super().clean()
        clave = datos.get('clave') or ''
        confirmacion = datos.get('confirmar_clave') or ''
        if not self.instance.pk and not clave:
            self.add_error('clave', 'Debes ingresar una contraseña al crear el funcionario.')
        if clave != confirmacion:
            self.add_error('confirmar_clave', 'Las contraseñas no coinciden.')
        if clave:
            candidato = User(username=datos.get('username', ''), first_name=datos.get('nombres', ''), last_name=datos.get('apellidos', ''), email=datos.get('correo', ''))
            from django.contrib.auth.password_validation import validate_password
            try:
                validate_password(clave, user=candidato)
            except ValidationError as exc:
                self.add_error('clave', exc)
        if self.instance.pk and self.actor and self.actor.pk == self.instance.usuario_id and not datos.get('activo_funcionario'):
            self.add_error('activo_funcionario', 'No puedes desactivar tu propia cuenta.')
        return datos

    @transaction.atomic
    def save(self, commit=True):
        if not commit:
            raise ValueError('FuncionarioForm requiere commit=True para mantener coherencia con User.')
        data = self.cleaned_data
        if self.instance.pk:
            user = self.instance.usuario
        else:
            user = User()
            user.is_staff = False
            user.is_superuser = False
        user.username = data['username']
        user.first_name = data['nombres']
        user.last_name = data['apellidos']
        user.email = data['correo']
        user.is_active = data['activo_funcionario']
        if data.get('clave'):
            user.set_password(data['clave'])
        user.save()
        self.instance.usuario = user
        perfil = super().save(commit=True)
        return perfil


_EXCLUSIONES = {
    ('organizacion', 'rol'): ['grupo'],
    ('organizacion', 'perfilusuario'): ['usuario'],
}


def formulario_para(modelo):
    if modelo == PerfilUsuario:
        return FuncionarioForm
    if modelo == Rol:
        return RolForm
    # Solo los campos editables declarados del modelo, nunca claves primarias automáticas.
    fields = [
        campo.name for campo in modelo._meta.get_fields()
        if (campo.concrete and not campo.auto_created and campo.editable)
    ]
    fields = [f for f in fields if f not in _EXCLUSIONES.get((modelo._meta.app_label, modelo._meta.model_name), ())]
    return modelform_factory(modelo, form=ModeloSGRForm, fields=fields)
