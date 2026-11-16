"""Completa códigos y relaciones de perfiles existentes sin borrar registros."""
from django.db import migrations


def completar_roles(apps, schema_editor):
    alias = schema_editor.connection.alias
    Rol = apps.get_model('organizacion', 'Rol')
    PerfilUsuario = apps.get_model('organizacion', 'PerfilUsuario')
    Through = PerfilUsuario.roles.through

    # Los roles de Evaluación 2 carecían de código. Cada PK preservada
    # genera un código único, sin alterar nombres, descripciones ni IDs.
    for rol in Rol.objects.using(alias).filter(codigo__isnull=True).iterator():
        rol.codigo = f'ROL-{rol.pk}'
        rol.save(update_fields=['codigo'], using=alias)

    # Conservar la asociación del campo rol original como rol de la lista.
    for perfil in PerfilUsuario.objects.using(alias).all().iterator():
        Through.objects.using(alias).get_or_create(
            perfilusuario_id=perfil.pk,
            rol_id=perfil.rol_id,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('organizacion', '0002_cargo_alter_perfilusuario_options_and_more'),
    ]

    operations = [migrations.RunPython(completar_roles, migrations.RunPython.noop)]
