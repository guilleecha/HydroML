from django.core.management.base import BaseCommand
from django.db import transaction
from projects.models import Project, DataSource
from experiments.models import MLExperiment, ExperimentSuite


class Command(BaseCommand):
    help = 'Clean database by deleting all Projects, DataSources, MLExperiments, and ExperimentSuites (preserves Users)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm the deletion without interactive prompt',
        )

    def handle(self, *args, **options):
        # Count existing objects
        project_count = Project.objects.count()
        datasource_count = DataSource.objects.count()
        experiment_count = MLExperiment.objects.count()
        suite_count = ExperimentSuite.objects.count()
        
        self.stdout.write(
            self.style.WARNING(f'\n=== DATABASE CLEANUP SUMMARY ===')
        )
        self.stdout.write(f'Projects to delete: {project_count}')
        self.stdout.write(f'DataSources to delete: {datasource_count}')
        self.stdout.write(f'MLExperiments to delete: {experiment_count}')
        self.stdout.write(f'ExperimentSuites to delete: {suite_count}')
        
        total_objects = project_count + datasource_count + experiment_count + suite_count
        
        if total_objects == 0:
            self.stdout.write(
                self.style.SUCCESS('\n✅ Database is already clean - no objects to delete.')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'\nTotal objects to delete: {total_objects}')
        )
        self.stdout.write(
            self.style.WARNING('⚠️  WARNING: This will permanently delete all test data!')
        )
        self.stdout.write(
            self.style.SUCCESS('✅ User accounts will be preserved.')
        )
        
        # Confirmation prompt
        if not options['confirm']:
            confirm = input('\nDo you want to proceed? (type "yes" to confirm): ')
            if confirm.lower() != 'yes':
                self.stdout.write(
                    self.style.ERROR('❌ Operation cancelled.')
                )
                return
        
        # Perform deletion in transaction
        try:
            with transaction.atomic():
                # Delete in reverse dependency order to avoid foreign key constraints
                deleted_suites = ExperimentSuite.objects.all().delete()[0]
                deleted_experiments = MLExperiment.objects.all().delete()[0]
                deleted_datasources = DataSource.objects.all().delete()[0]
                deleted_projects = Project.objects.all().delete()[0]
                
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ DATABASE CLEANUP COMPLETED:')
                )
                self.stdout.write(f'  • {deleted_projects} Projects deleted')
                self.stdout.write(f'  • {deleted_datasources} DataSources deleted') 
                self.stdout.write(f'  • {deleted_experiments} MLExperiments deleted')
                self.stdout.write(f'  • {deleted_suites} ExperimentSuites deleted')
                self.stdout.write(
                    self.style.SUCCESS(f'  • User accounts preserved ✅')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during cleanup: {e}')
            )
            raise
