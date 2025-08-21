"""
Pytest configuration and fixtures for Data Studio testing
Provides shared fixtures and test utilities for comprehensive testing
"""

import pytest
import tempfile
import pandas as pd
from unittest.mock import Mock, patch
from django.contrib.auth.models import User
from django.test import Client
from django.conf import settings
from django.core.cache import cache
from rest_framework.test import APIClient

from projects.models import Project, DataSource
from data_tools.services.api_performance_service import rate_limiter, api_cache, performance_monitor


@pytest.fixture
def test_user():
    """Create a test user for authentication"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpassword123'
    )


@pytest.fixture
def test_project(test_user):
    """Create a test project"""
    return Project.objects.create(
        name='Test Project',
        owner=test_user,
        description='Project for testing Data Studio features'
    )


@pytest.fixture
def test_datasource(test_project):
    """Create a test datasource with ready status"""
    return DataSource.objects.create(
        name='Test DataSource',
        project=test_project,
        status=DataSource.Status.READY,
        description='DataSource for comprehensive testing'
    )


@pytest.fixture
def test_datasource_with_data(test_project, tmp_path):
    """Create a test datasource with actual data file"""
    # Create sample data
    df = pd.DataFrame({
        'id': range(1, 101),
        'name': [f'User_{i}' for i in range(1, 101)],
        'age': [20 + (i % 60) for i in range(100)],
        'city': ['New York', 'London', 'Tokyo', 'Paris', 'Sydney'] * 20,
        'score': [75.5 + (i % 25) for i in range(100)]
    })
    
    # Save to temporary file
    data_file = tmp_path / "test_data.parquet"
    df.to_parquet(data_file, index=False)
    
    datasource = DataSource.objects.create(
        name='Test DataSource with Data',
        project=test_project,
        status=DataSource.Status.READY,
        description='DataSource with sample data for testing'
    )
    
    # Mock the file path
    with patch.object(datasource, 'file') as mock_file:
        mock_file.path = str(data_file)
        yield datasource, df


@pytest.fixture
def api_client(test_user):
    """Create an authenticated API client"""
    client = APIClient()
    client.force_authenticate(user=test_user)
    return client


@pytest.fixture
def django_client(test_user):
    """Create an authenticated Django test client"""
    client = Client()
    client.force_login(test_user)
    return client


@pytest.fixture
def clear_cache():
    """Clear all caches before and after test"""
    cache.clear()
    api_cache.clear_pattern('*')
    yield
    cache.clear()
    api_cache.clear_pattern('*')


@pytest.fixture
def reset_rate_limiter():
    """Reset rate limiter state before and after test"""
    rate_limiter.requests.clear()
    yield
    rate_limiter.requests.clear()


@pytest.fixture
def reset_performance_monitor():
    """Reset performance monitor state"""
    performance_monitor.metrics.clear()
    yield
    performance_monitor.metrics.clear()


@pytest.fixture
def mock_session_manager():
    """Mock session manager for testing"""
    with patch('data_tools.services.session_manager.get_session_manager') as mock:
        session_manager = Mock()
        
        # Configure default mock behavior
        session_manager.get_session_info.return_value = {
            'session_exists': True,
            'session_id': 'test-session-id',
            'history_length': 5,
            'current_position': 2,
            'current_shape': [100, 10]
        }
        session_manager.get_current_dataframe.return_value = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        session_manager.initialize_session.return_value = True
        session_manager.undo_operation.return_value = True
        session_manager.redo_operation.return_value = True
        
        mock.return_value = session_manager
        yield session_manager


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing"""
    return pd.DataFrame({
        'id': range(1, 11),
        'name': [f'Item_{i}' for i in range(1, 11)],
        'category': ['A', 'B', 'C'] * 3 + ['A'],
        'value': [10.5 + i for i in range(10)],
        'is_active': [True, False] * 5
    })


@pytest.fixture
def pagination_test_data():
    """Generate test data for pagination testing"""
    return {
        'total_rows': 1000,
        'page_sizes': [10, 25, 50, 100],
        'test_pages': [1, 2, 5, 10, 20],
        'expected_responses': {
            'page_1_size_25': {'start_row': 1, 'end_row': 25},
            'page_2_size_25': {'start_row': 26, 'end_row': 50},
            'page_5_size_10': {'start_row': 41, 'end_row': 50}
        }
    }


@pytest.fixture
def filter_test_data():
    """Generate test data for filter testing"""
    return {
        'columns': ['name', 'age', 'city', 'score'],
        'filter_types': ['text', 'range', 'multiselect', 'boolean'],
        'sample_filters': {
            'text_filter': {'column': 'name', 'type': 'text', 'value': 'User_1'},
            'range_filter': {'column': 'age', 'type': 'range', 'min': 25, 'max': 45},
            'multiselect_filter': {'column': 'city', 'type': 'multiselect', 'values': ['New York', 'London']},
            'boolean_filter': {'column': 'is_active', 'type': 'boolean', 'value': True}
        }
    }


@pytest.fixture
def websocket_test_config():
    """Configuration for WebSocket testing"""
    return {
        'connection_timeout': 5.0,
        'message_timeout': 2.0,
        'test_messages': [
            {'type': 'ping'},
            {'type': 'subscribe_to_operation', 'operation_id': 'test-op-123'},
            {'type': 'request_session_status'}
        ],
        'expected_responses': [
            {'type': 'pong'},
            {'type': 'subscription_confirmed'},
            {'type': 'session_status'}
        ]
    }


@pytest.fixture
def bulk_operation_test_data():
    """Test data for bulk operations"""
    return {
        'operation_types': ['delete_rows', 'update_cells', 'apply_transformations', 'column_operations'],
        'test_operations': {
            'delete_rows': {
                'operation_type': 'delete_rows',
                'items': [1, 2, 3, 4, 5],
                'options': {'batch_size': 2}
            },
            'update_cells': {
                'operation_type': 'update_cells',
                'items': [
                    {'row_index': 0, 'column': 'name', 'value': 'Updated Name'},
                    {'row_index': 1, 'column': 'age', 'value': 30}
                ],
                'options': {'batch_size': 1}
            },
            'column_operations': {
                'operation_type': 'column_operations',
                'items': [
                    {'type': 'add_column', 'parameters': {'name': 'new_column', 'default_value': 'default'}},
                    {'type': 'drop_columns', 'parameters': {'columns': ['old_column']}}
                ],
                'options': {'batch_size': 1}
            }
        }
    }


@pytest.fixture
def performance_test_config():
    """Configuration for performance testing"""
    return {
        'load_test_requests': 50,
        'concurrent_users': 10,
        'response_time_threshold': 2.0,  # seconds
        'success_rate_threshold': 0.95,  # 95%
        'memory_threshold': 100,  # MB
        'cpu_threshold': 80,  # %
        'endpoints_to_test': [
            'get_session_status',
            'data_studio_pagination_api',
            'bulk_operations_api'
        ]
    }


# Custom pytest markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests between components"  
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end workflow tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and load tests"
    )
    config.addinivalue_line(
        "markers", "websocket: WebSocket functionality tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer to execute"
    )


# Test utilities
class DataStudioTestUtils:
    """Utility class for common test operations"""
    
    @staticmethod
    def create_test_session(user_id, datasource_id):
        """Create a test session with mock data"""
        return {
            'user_id': user_id,
            'datasource_id': datasource_id,
            'session_id': 'test-session',
            'is_active': True,
            'operations': [],
            'current_position': 0
        }
    
    @staticmethod
    def create_mock_dataframe(rows=100, columns=5):
        """Create a mock DataFrame for testing"""
        data = {}
        for i in range(columns):
            data[f'col_{i}'] = [f'value_{i}_{j}' for j in range(rows)]
        return pd.DataFrame(data)
    
    @staticmethod
    def assert_api_response_structure(response_data, required_keys):
        """Assert that API response has required structure"""
        assert isinstance(response_data, dict)
        for key in required_keys:
            assert key in response_data, f"Missing required key: {key}"
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """Measure execution time of a function"""
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        return result, execution_time
    
    @staticmethod
    def simulate_large_dataset(rows=10000, columns=20):
        """Simulate a large dataset for performance testing"""
        import random
        data = {}
        
        for i in range(columns):
            if i % 4 == 0:  # Numeric columns
                data[f'numeric_{i}'] = [random.random() * 100 for _ in range(rows)]
            elif i % 4 == 1:  # String columns
                data[f'string_{i}'] = [f'text_{j}_{random.randint(1, 1000)}' for j in range(rows)]
            elif i % 4 == 2:  # Categorical columns
                categories = ['Category_A', 'Category_B', 'Category_C', 'Category_D']
                data[f'category_{i}'] = [random.choice(categories) for _ in range(rows)]
            else:  # Boolean columns
                data[f'boolean_{i}'] = [random.choice([True, False]) for _ in range(rows)]
        
        return pd.DataFrame(data)


@pytest.fixture
def test_utils():
    """Provide test utilities to tests"""
    return DataStudioTestUtils


# Database fixtures for specific test scenarios
@pytest.fixture(scope='function')
@pytest.mark.django_db
def db_with_test_data(test_user):
    """Create database with comprehensive test data"""
    projects = []
    datasources = []
    
    # Create multiple projects and datasources for testing
    for i in range(3):
        project = Project.objects.create(
            name=f'Test Project {i+1}',
            owner=test_user,
            description=f'Test project {i+1} for comprehensive testing'
        )
        projects.append(project)
        
        # Create multiple datasources per project
        for j in range(2):
            datasource = DataSource.objects.create(
                name=f'DataSource {j+1} - Project {i+1}',
                project=project,
                status=DataSource.Status.READY,
                description=f'Test datasource {j+1} for project {i+1}'
            )
            datasources.append(datasource)
    
    return {
        'user': test_user,
        'projects': projects,
        'datasources': datasources
    }