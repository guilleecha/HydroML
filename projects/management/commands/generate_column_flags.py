# projects/management/commands/generate_column_flags.py
from django.core.management.base import BaseCommand
from projects.models import DataSource
from projects.utils.column_analyzer import ColumnAnalyzer
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate column flags for existing datasources'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration of flags even if they already exist'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of datasources to process'
        )
        parser.add_argument(
            '--datasource-id',
            type=str,
            help='Process specific datasource by ID'
        )
    
    def handle(self, *args, **options):
        force = options['force']
        limit = options['limit']
        datasource_id = options['datasource_id']
        
        self.stdout.write('🔍 Starting column flags generation...')
        
        # Filter datasources
        queryset = DataSource.objects.filter(status=DataSource.Status.READY)
        
        if datasource_id:
            try:
                queryset = queryset.filter(id=datasource_id)
                if not queryset.exists():
                    self.stdout.write(
                        self.style.ERROR(f'❌ DataSource {datasource_id} not found')
                    )
                    return
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f'❌ Invalid UUID: {datasource_id}')
                )
                return
        
        if not force:
            # Only process datasources without flags
            queryset = queryset.filter(column_flags__isnull=True)
        
        if limit:
            queryset = queryset[:limit]
        
        total_count = queryset.count()
        self.stdout.write(f'📊 Found {total_count} datasources to process')
        
        if total_count == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ No datasources need processing')
            )
            return
        
        success_count = 0
        error_count = 0
        
        for i, datasource in enumerate(queryset, 1):
            self.stdout.write(f'🔄 [{i}/{total_count}] Processing: {datasource.name}')
            
            try:
                with transaction.atomic():
                    flags = ColumnAnalyzer.update_datasource_flags(datasource, force_update=force)
                    
                    if flags:
                        columns_count = len([k for k in flags.keys() if not k.startswith('_')])
                        self.stdout.write(
                            self.style.SUCCESS(f'   ✅ Generated flags for {columns_count} columns')
                        )
                        success_count += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'   ⚠️  No flags generated (empty dataset?)')
                        )
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Error: {str(e)}')
                )
                error_count += 1
                logger.exception(f'Error processing datasource {datasource.id}')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'📋 SUMMARY:')
        self.stdout.write(f'   ✅ Successfully processed: {success_count}')
        self.stdout.write(f'   ❌ Errors: {error_count}')
        self.stdout.write(f'   📊 Total: {total_count}')
        
        if success_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Successfully generated flags for {success_count} datasources!')
            )
        
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f'\n⚠️  {error_count} datasources had errors. Check logs for details.')
            )