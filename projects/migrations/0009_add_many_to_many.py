# Generated migration - Step 2: Add many-to-many relationship

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_add_datasource_owner'),
    ]

    operations = [
        # Add the many-to-many field to Project
        migrations.AddField(
            model_name='project',
            name='datasources',
            field=models.ManyToManyField(
                blank=True,
                help_text='DataSources associated with this project',
                related_name='projects',
                to='projects.datasource'
            ),
        ),
    ]
