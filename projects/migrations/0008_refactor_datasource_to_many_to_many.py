# Generated migration for DataSource to Project many-to-many refactoring

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


def populate_m2m_relationships(apps, schema_editor):
    """
    Populate the new many-to-many relationship table with existing relationships.
    """
    Project = apps.get_model('projects', 'Project')
    DataSource = apps.get_model('projects', 'DataSource')
    
    relationships_created = 0
    for project in Project.objects.all():
        # Get all DataSources that belonged to this project
        project_datasources = DataSource.objects.filter(project=project)
        for datasource in project_datasources:
            project.datasources.add(datasource)
            relationships_created += 1
    
    print(f"Created {relationships_created} many-to-many relationships")


def reverse_populate_foreign_keys(apps, schema_editor):
    """
    Reverse migration: populate foreign keys from many-to-many relationships.
    """
    Project = apps.get_model('projects', 'Project')
    DataSource = apps.get_model('projects', 'DataSource')
    
    # For each DataSource, set its project to the first project it's associated with
    for datasource in DataSource.objects.all():
        projects = datasource.projects.all()
        if projects.exists():
            datasource.project_id = projects.first().id
            datasource.save(update_fields=['project'])


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
        
        # Step 4: Add the many-to-many field to Project
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
        
        # Step 5: Populate the many-to-many relationships
        migrations.RunPython(
            code=populate_m2m_relationships,
            reverse_code=reverse_populate_foreign_keys,
        ),
        
        # Step 6: Remove the old project foreign key
        migrations.RemoveField(
            model_name='datasource',
            name='project',
        ),
    ]
