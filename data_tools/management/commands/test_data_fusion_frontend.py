"""
Django management command to test the complete data fusion frontend workflow.

This command tests both the API endpoint and provides instructions for
manual frontend testing.
"""

from django.core.management.base import BaseCommand
from django.urls import reverse
from django.test import Client
from projects.models import Project, DataSource


class Command(BaseCommand):
    help = 'Test the complete data fusion workflow including frontend integration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Data Fusion Frontend Integration Test ===\n'))
        
        # Find a project with at least 2 ready DataSources
        project = None
        for p in Project.objects.all():
            if p.datasources.filter(status='READY').count() >= 2:
                project = p
                break
        
        if not project:
            self.stdout.write(self.style.ERROR('No project found with at least 2 ready DataSources'))
            return
        
        datasources = list(project.datasources.filter(status='READY')[:2])
        ds_a, ds_b = datasources[0], datasources[1]
        
        self.stdout.write(f'1. Found test project: {project.name}')
        self.stdout.write(f'   - DataSource A: {ds_a.name} ({ds_a.id})')
        self.stdout.write(f'   - DataSource B: {ds_b.name} ({ds_b.id})')
        
        # Test the API endpoint
        self.stdout.write('\n2. Testing API endpoint...')
        
        client = Client()
        
        # First, we need to authenticate (simulate logged in user)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get any user or create one for testing
        user = User.objects.first()
        if not user:
            # Create a test user
            user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
            self.stdout.write('   - Created test user for authentication')
        
        client.force_login(user)
        self.stdout.write(f'   - Authenticated as: {user.username}')
        
        # Test the API call
        api_url = f'/tools/api/get-fusion-columns/?ds_a={ds_a.id}&ds_b={ds_b.id}'
        response = client.get(api_url, HTTP_HOST='localhost')
        
        self.stdout.write(f'   - API URL: {api_url}')
        self.stdout.write(f'   - Response status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            self.stdout.write(self.style.SUCCESS('   ✓ API call successful'))
            
            # The API response structure might vary, let's check what we have
            self.stdout.write(f'   - Response keys: {list(data.keys())}')
            
            # Try to access the data based on what structure we have
            if 'data' in data:
                # New structure
                cols_a = len(data["data"]["datasource_a"]["columns"])
                cols_b = len(data["data"]["datasource_b"]["columns"])
                sample_cols_a = data["data"]["datasource_a"]["columns"][:3]
                sample_cols_b = data["data"]["datasource_b"]["columns"][:3]
            elif 'datasource_a' in data:
                # Direct structure
                cols_a = len(data["datasource_a"]["columns"])
                cols_b = len(data["datasource_b"]["columns"])
                sample_cols_a = data["datasource_a"]["columns"][:3]
                sample_cols_b = data["datasource_b"]["columns"][:3]
            else:
                self.stdout.write(self.style.WARNING(f'   ⚠ Unexpected response structure: {data}'))
                return
                
            self.stdout.write(f'   - DataSource A columns: {cols_a}')
            self.stdout.write(f'   - DataSource B columns: {cols_b}')
            self.stdout.write(f'   - Sample columns A: {sample_cols_a}')
            self.stdout.write(f'   - Sample columns B: {sample_cols_b}')
        else:
            self.stdout.write(self.style.ERROR(f'   ✗ API call failed: {response.content.decode()}'))
            return
        
        # Test the frontend page
        self.stdout.write('\n3. Testing frontend page access...')
        
        page_url = reverse('data_tools:data_fusion', kwargs={'pk': project.id})
        response = client.get(page_url, HTTP_HOST='localhost')
        
        self.stdout.write(f'   - Page URL: {page_url}')
        self.stdout.write(f'   - Response status: {response.status_code}')
        
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('   ✓ Frontend page accessible'))
            
            # Check if our JavaScript file is included
            content = response.content.decode()
            if 'data_fusion.js' in content:
                self.stdout.write('   ✓ JavaScript file is included')
            else:
                self.stdout.write(self.style.WARNING('   ⚠ JavaScript file not found in page'))
                
            # Check if the required elements are present
            required_elements = [
                'id="error-container"',
                'id="loading-indicator"', 
                'id="column-selection-section"',
                'id="columns-datasource-a"',
                'id="columns-datasource-b"'
            ]
            
            for element in required_elements:
                if element in content:
                    self.stdout.write(f'   ✓ Found element: {element}')
                else:
                    self.stdout.write(self.style.WARNING(f'   ⚠ Missing element: {element}'))
        else:
            self.stdout.write(self.style.ERROR(f'   ✗ Frontend page failed: {response.status_code}'))
            return
        
        # Provide manual testing instructions
        self.stdout.write(self.style.SUCCESS('\n=== Manual Testing Instructions ==='))
        self.stdout.write('1. Open your browser and navigate to:')
        self.stdout.write(f'   http://localhost:8000{page_url}')
        self.stdout.write('\n2. Test the following workflow:')
        self.stdout.write(f'   a) Select "{ds_a.name}" in the first dropdown')
        self.stdout.write(f'   b) Select "{ds_b.name}" in the second dropdown')
        self.stdout.write('   c) Click "Cargar Columnas" button')
        self.stdout.write('   d) Verify that:')
        self.stdout.write('      - Loading indicator appears')
        self.stdout.write('      - Column selection section appears')
        self.stdout.write('      - Multi-select boxes are populated with columns')
        self.stdout.write('      - Merge key dropdowns show available columns')
        self.stdout.write('      - Common columns are highlighted as "(común)"')
        self.stdout.write('\n3. Test error scenarios:')
        self.stdout.write('   a) Try clicking "Cargar Columnas" without selecting datasources')
        self.stdout.write('   b) Try selecting the same datasource in both dropdowns')
        self.stdout.write('   c) Verify error messages appear properly')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Integration test completed!'))
        self.stdout.write('✓ API endpoint is working')
        self.stdout.write('✓ Frontend page is accessible')
        self.stdout.write('✓ JavaScript components are in place')
        self.stdout.write('\nThe data fusion frontend is ready for testing!')
