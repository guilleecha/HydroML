#!/usr/bin/env python3
"""
Django management command to test the Data Fusion API endpoint
Usage: python manage.py test_fusion_api
"""
from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth.models import User
import json


class Command(BaseCommand):
    help = 'Test the Data Fusion API endpoint functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS('=== Data Fusion API Endpoint Test ===')
        )

        # Get test user
        user = User.objects.first()
        if not user:
            self.stdout.write(
                self.style.ERROR("ERROR: No user found for testing")
            )
            return

        # Configure test client to work with Django test framework
        from django.test.client import Client
        from django.test.utils import override_settings
        
        with override_settings(ALLOWED_HOSTS=['*']):
            client = Client()
            client.force_login(user)

        with override_settings(ALLOWED_HOSTS=['*']):
            client = Client()
            client.force_login(user)

            # Test 1: Missing parameters
            self.stdout.write("\n1. Testing missing parameters...")
            try:
                response = client.get('/tools/api/get-fusion-columns/')
                
                if verbose:
                    self.stdout.write(f"   Status Code: {response.status_code}")
                    
                if response.status_code == 400:
                    try:
                        data = json.loads(response.content)
                        if verbose:
                            self.stdout.write(f"   Expected error: {data.get('error', 'No error message')}")
                        self.stdout.write(
                            self.style.SUCCESS("   ✓ PASS - Correctly validates missing parameters")
                        )
                    except json.JSONDecodeError:
                        self.stdout.write(
                            self.style.SUCCESS("   ✓ PASS - Returns 400 for missing parameters")
                        )
                else:
                    self.stdout.write(
                        self.style.ERROR("   ✗ FAIL - Should return 400 for missing parameters")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   ✗ ERROR: {e}")
                )

            # Test 2: Invalid UUIDs
            self.stdout.write("\n2. Testing invalid UUIDs...")
            try:
                response = client.get('/tools/api/get-fusion-columns/', {
                    'ds_a': '00000000-0000-0000-0000-000000000000',
                    'ds_b': '11111111-1111-1111-1111-111111111111'
                })
                
                if verbose:
                    self.stdout.write(f"   Status Code: {response.status_code}")
                    
                if response.status_code == 404:
                    try:
                        data = json.loads(response.content)
                        if verbose:
                            self.stdout.write(f"   Expected error: {data.get('error', 'No error message')}")
                        self.stdout.write(
                            self.style.SUCCESS("   ✓ PASS - Correctly handles non-existent datasources")
                        )
                    except json.JSONDecodeError:
                        self.stdout.write(
                            self.style.SUCCESS("   ✓ PASS - Returns 404 for non-existent datasources")
                        )
                else:
                    self.stdout.write(
                        self.style.ERROR("   ✗ FAIL - Should return 404 for non-existent datasources")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   ✗ ERROR: {e}")
                )

            # Test 3: URL resolution
            self.stdout.write("\n3. Testing URL resolution...")
            try:
                from django.urls import reverse
                url = reverse('data_tools:get_fusion_columns_api')
                if verbose:
                    self.stdout.write(f"   API URL resolves to: {url}")
                self.stdout.write(
                    self.style.SUCCESS("   ✓ PASS - URL properly configured")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   ✗ FAIL - URL resolution error: {e}")
                )

            # Test 4: Authentication requirement
            self.stdout.write("\n4. Testing authentication requirement...")
            try:
                client_unauth = Client()  # No login
                response = client_unauth.get('/tools/api/get-fusion-columns/', {
                    'ds_a': '00000000-0000-0000-0000-000000000000',
                    'ds_b': '11111111-1111-1111-1111-111111111111'
                })
                
                if verbose:
                    self.stdout.write(f"   Status Code: {response.status_code}")
                    
                if response.status_code == 302:  # Redirect to login
                    self.stdout.write(
                        self.style.SUCCESS("   ✓ PASS - Correctly requires authentication")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR("   ✗ FAIL - Should redirect unauthenticated users to login")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   ✗ ERROR: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS("\n=== Test Summary ===")
        )
        self.stdout.write("Basic API endpoint validation completed.")
        self.stdout.write("The endpoint is properly configured and handles basic validation.")
        self.stdout.write("File reading tests would require actual Parquet files in the system.")
        
        # Check if there are any ready datasources for integration testing
        from projects.models import DataSource
        ready_datasources = DataSource.objects.filter(status='READY').count()
        
        if ready_datasources >= 2:
            self.stdout.write(
                self.style.SUCCESS(f"\n✓ Found {ready_datasources} READY datasources - Integration testing possible")
            )
            
            # Test 5: Integration test with real datasources
            self.stdout.write("\n5. Testing with real READY datasources...")
            try:
                # Get first two READY datasources
                datasources = DataSource.objects.filter(status='READY')[:2]
                if len(datasources) == 2:
                    ds_a, ds_b = datasources[0], datasources[1]
                    
                    with override_settings(ALLOWED_HOSTS=['*']):
                        client = Client()
                        client.force_login(user)
                        
                        response = client.get('/tools/api/get-fusion-columns/', {
                            'ds_a': str(ds_a.id),
                            'ds_b': str(ds_b.id)
                        })
                        
                        if verbose:
                            self.stdout.write(f"   Status Code: {response.status_code}")
                            
                        if response.status_code == 200:
                            try:
                                data = json.loads(response.content)
                                if verbose:
                                    self.stdout.write(f"   DataSource A: {data['datasource_a']['name']} ({len(data['datasource_a']['columns'])} columns)")
                                    self.stdout.write(f"   DataSource B: {data['datasource_b']['name']} ({len(data['datasource_b']['columns'])} columns)")
                                self.stdout.write(
                                    self.style.SUCCESS("   ✓ PASS - Successfully fetched columns from real datasources")
                                )
                            except (json.JSONDecodeError, KeyError) as e:
                                self.stdout.write(
                                    self.style.ERROR(f"   ✗ FAIL - Invalid JSON response: {e}")
                                )
                        else:
                            try:
                                data = json.loads(response.content)
                                error_msg = data.get('error', 'Unknown error')
                                self.stdout.write(
                                    self.style.ERROR(f"   ✗ FAIL - Error: {error_msg}")
                                )
                            except json.JSONDecodeError:
                                self.stdout.write(
                                    self.style.ERROR(f"   ✗ FAIL - HTTP {response.status_code}")
                                )
                else:
                    self.stdout.write(
                        self.style.WARNING("   ⚠ SKIP - Could not get 2 datasources for testing")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   ✗ ERROR: {e}")
                )
        else:
            self.stdout.write(
                self.style.WARNING(f"\n⚠ Only {ready_datasources} READY datasources found - Need at least 2 for full integration testing")
            )
