#!/usr/bin/env python3
"""
Django management command to convert all DataSource files to Parquet format
Usage: python manage.py convert_datasources_to_parquet
"""
import os
import pandas as pd
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from projects.models import DataSource


class Command(BaseCommand):
    help = 'Convert all DataSource files to Parquet format for consistency and performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be converted without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force conversion even if target Parquet file already exists',
        )
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Keep original files as backup (rename with .backup extension)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force_conversion = options['force']
        keep_backup = options['backup']
        
        self.stdout.write(
            self.style.SUCCESS('=== DataSource Parquet Conversion Utility ===')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )

        # Get all DataSources
        datasources = DataSource.objects.all()
        total_count = datasources.count()
        
        if total_count == 0:
            self.stdout.write(
                self.style.WARNING('No DataSources found in the database')
            )
            return

        self.stdout.write(f'\nFound {total_count} DataSources to process...\n')

        converted_count = 0
        skipped_count = 0
        error_count = 0

        for ds in datasources:
            try:
                result = self._process_datasource(ds, dry_run, force_conversion, keep_backup)
                if result == 'converted':
                    converted_count += 1
                elif result == 'skipped':
                    skipped_count += 1
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'ERROR processing DataSource "{ds.name}" (ID: {ds.id}): {e}')
                )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(f'\n=== Conversion Summary ===')
        )
        self.stdout.write(f'Total DataSources: {total_count}')
        self.stdout.write(
            self.style.SUCCESS(f'✓ Converted: {converted_count}')
        )
        self.stdout.write(
            self.style.WARNING(f'⚠ Skipped: {skipped_count}')
        )
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f'✗ Errors: {error_count}')
            )
        else:
            self.stdout.write('✓ No errors encountered')

        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nDRY RUN completed - run without --dry-run to apply changes')
            )

    def _process_datasource(self, ds, dry_run, force_conversion, keep_backup):
        """
        Process a single DataSource for Parquet conversion
        Returns: 'converted', 'skipped', or raises exception
        """
        if not ds.file:
            self.stdout.write(
                self.style.WARNING(f'⚠ Skipping DataSource "{ds.name}" - No file attached')
            )
            return 'skipped'

        original_path = Path(ds.file.path)
        
        # Check if file exists
        if not original_path.exists():
            self.stdout.write(
                self.style.ERROR(f'✗ File not found: {original_path}')
            )
            raise FileNotFoundError(f'DataSource file does not exist: {original_path}')

        # Check if already in Parquet format
        if original_path.suffix.lower() == '.parquet':
            self.stdout.write(
                self.style.SUCCESS(f'✓ Skipping "{ds.name}" - Already in Parquet format')
            )
            return 'skipped'

        # Determine new Parquet path
        parquet_path = original_path.with_suffix('.parquet')
        
        # Check if target Parquet file already exists
        if parquet_path.exists() and not force_conversion:
            self.stdout.write(
                self.style.WARNING(f'⚠ Skipping "{ds.name}" - Parquet file already exists: {parquet_path.name}')
            )
            self.stdout.write(f'   Use --force to overwrite existing Parquet files')
            return 'skipped'

        self.stdout.write(f'🔄 Converting "{ds.name}": {original_path.name} → {parquet_path.name}')

        if dry_run:
            self.stdout.write(f'   [DRY RUN] Would convert: {original_path} → {parquet_path}')
            return 'converted'

        # Perform the actual conversion
        try:
            # Read the original file based on its extension
            df = self._read_file(original_path)
            
            # Save as Parquet
            df.to_parquet(parquet_path, index=False)
            
            # Update DataSource file path
            with transaction.atomic():
                # Calculate the new relative path for Django's FileField
                media_root = Path(ds.file.storage.location)
                relative_parquet_path = parquet_path.relative_to(media_root)
                ds.file.name = str(relative_parquet_path)
                ds.save(update_fields=['file'])

            # Handle backup if requested
            if keep_backup:
                backup_path = original_path.with_suffix(original_path.suffix + '.backup')
                original_path.rename(backup_path)
                self.stdout.write(f'   📦 Original file backed up as: {backup_path.name}')
            else:
                # Remove original file
                original_path.unlink()
                self.stdout.write(f'   🗑️ Removed original file: {original_path.name}')

            self.stdout.write(
                self.style.SUCCESS(f'   ✅ Successfully converted "{ds.name}" to Parquet format')
            )
            
            # Verify the conversion
            self._verify_parquet_file(parquet_path, ds.name)
            
            return 'converted'

        except Exception as e:
            # Clean up on error
            if parquet_path.exists():
                parquet_path.unlink()
            raise Exception(f'Conversion failed: {e}')

    def _read_file(self, file_path):
        """
        Read a file into a pandas DataFrame based on its extension
        """
        extension = file_path.suffix.lower()
        
        if extension == '.csv':
            # Try different encodings for CSV files
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    return pd.read_csv(file_path, encoding=encoding)
                except UnicodeDecodeError:
                    continue
            # If all encodings fail, try with error handling
            return pd.read_csv(file_path, encoding='utf-8', errors='replace')
            
        elif extension in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
            
        elif extension == '.json':
            return pd.read_json(file_path)
            
        elif extension == '.tsv':
            return pd.read_csv(file_path, sep='\t')
            
        else:
            # Default to CSV parsing for unknown extensions
            self.stdout.write(
                self.style.WARNING(f'   ⚠ Unknown file extension {extension}, attempting CSV parsing')
            )
            return pd.read_csv(file_path)

    def _verify_parquet_file(self, parquet_path, datasource_name):
        """
        Verify that the Parquet file was created correctly and is readable
        """
        try:
            df_verify = pd.read_parquet(parquet_path)
            row_count = len(df_verify)
            col_count = len(df_verify.columns)
            file_size = parquet_path.stat().st_size
            
            self.stdout.write(
                f'   📊 Verified: {row_count:,} rows, {col_count} columns, {file_size:,} bytes'
            )
            
        except Exception as e:
            raise Exception(f'Parquet file verification failed for {datasource_name}: {e}')
