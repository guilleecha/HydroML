# Generated migration - Step 1: Add owner field to DataSource

from django.db import migrations, models
from django.conf import settings


def populate_datasource_owners(apps, schema_editor):
    """
    Set the owner of each DataSource to be the owner of its project.
    """
    DataSource = apps.get_model('projects', 'DataSource')
    
    updated_count = 0
    for datasource in DataSource.objects.select_related('project').all():
        if hasattr(datasource, 'project') and datasource.project:
            datasource.owner = datasource.project.owner
            datasource.save(update_fields=['owner'])
            updated_count += 1
    
    print(f"Updated owner for {updated_count} DataSources")


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_project_is_favorite'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Step 1: Add the owner field to DataSource (nullable temporarily)
        migrations.AddField(
            model_name='datasource',
            name='owner',
            field=models.ForeignKey(
                help_text='User who owns this DataSource',
                null=True,
                blank=True,
                on_delete=models.CASCADE,
                related_name='owned_datasources',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        
        # Step 2: Populate owner field based on project ownership
        migrations.RunPython(
            code=populate_datasource_owners,
            reverse_code=migrations.RunPython.noop,
        ),
        
        # Step 3: Make owner field non-nullable
        migrations.AlterField(
            model_name='datasource',
            name='owner',
            field=models.ForeignKey(
                help_text='User who owns this DataSource',
                on_delete=models.CASCADE,
                related_name='owned_datasources',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
