# Generated by Django 3.2.8 on 2021-12-07 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('package_id', models.TextField(unique=True)),
                ('version', models.TextField()),
                ('file_path', models.TextField()),
                ('is_secret', models.BooleanField(default=False)),
                ('github_url', models.TextField(default='')),
                ('js_program', models.TextField(default='')),
            ],
        ),
        migrations.AddConstraint(
            model_name='package',
            constraint=models.UniqueConstraint(fields=('name', 'version'), name='uniquePackage'),
        ),
    ]
