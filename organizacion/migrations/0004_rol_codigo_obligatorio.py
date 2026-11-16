"""Exige código en nuevos roles una vez completados los históricos."""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('organizacion', '0003_completar_codigos_roles_historicos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rol',
            name='codigo',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
