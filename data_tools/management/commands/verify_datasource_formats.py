#!/usr/bin/env python3
"""
Django management command to verify DataSource file formats
Usage: python manage.py verify_datasource_formats
"""
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from projects.models import DataSource


class Command(BaseCommand):
    help = 'Verify the file formats of all DataSources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--show-details',
            action='store_true',
            help='Show detailed information about each DataSource',
        )

    def handle(self, *args, **options):
        show_details = options['show_details']
        
        self.stdout.write(
            self.style.SUCCESS('=== DataSource Format Verification ===')
        )

        datasources = DataSource.objects.all()
        total_count = datasources.count()
        
        if total_count == 0:
            self.stdout.write(
                self.style.WARNING('No DataSources found in the database')
            )
            return

        parquet_count = 0
        other_formats = []
        missing_files = []

        self.stdout.write(f'\nChecking {total_count} DataSources...\n')

        for ds in datasources:
            if not ds.file:
                missing_files.append(ds.name)
                self.stdout.write(
                    self.style.ERROR(f'✗ {ds.name} - No file attached')
                )
                continue

            file_path = Path(ds.file.path)
            
            if not file_path.exists():
                missing_files.append(ds.name)
                self.stdout.write(
                    self.style.ERROR(f'✗ {ds.name} - File not found: {file_path}')
                )
                continue

            extension = file_path.suffix.lower()
            file_size = file_path.stat().st_size
            
            if extension == '.parquet':
                parquet_count += 1
                if show_details:
                    try:
                        import pandas as pd
                        df = pd.read_parquet(file_path)
                        rows, cols = df.shape
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ {ds.name} - Parquet ({file_size:,} bytes, {rows:,} rows, {cols} columns)')
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'✗ {ds.name} - Parquet file corrupted: {e}')
                        )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ {ds.name} - Parquet format ({file_size:,} bytes)')
                    )
            else:
                other_formats.append((ds.name, extension, file_size))
                self.stdout.write(
                    self.style.WARNING(f'⚠ {ds.name} - {extension.upper()} format ({file_size:,} bytes)')
                )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(f'\n=== Format Summary ===')
        )
        self.stdout.write(f'Total DataSources: {total_count}')
        self.stdout.write(
            self.style.SUCCESS(f'✓ Parquet format: {parquet_count}')
        )
        
        if other_formats:
            self.stdout.write(
                self.style.WARNING(f'⚠ Other formats: {len(other_formats)}')
            )
            for name, ext, size in other_formats:
                self.stdout.write(f'   - {name}: {ext.upper()} ({size:,} bytes)')
        
        if missing_files:
            self.stdout.write(
                self.style.ERROR(f'✗ Missing files: {len(missing_files)}')
            )
            for name in missing_files:
                self.stdout.write(f'   - {name}')

        if parquet_count == total_count and not missing_files:
            self.stdout.write(
                self.style.SUCCESS('\n🎉 All DataSources are in Parquet format!')
            )
        elif other_formats:
            self.stdout.write(
                self.style.WARNING(f'\n💡 Run "python manage.py convert_datasources_to_parquet" to convert remaining files')
            )
