"""
Comprehensive tests for the DataStudioSessionManager system.
Tests security, performance, functionality, and integration.
"""

import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import cache

from data_tools.services.session_manager import (
    DataStudioSessionManager, get_session_manager
)
from data_tools.services.session_metadata import SessionConfig, SessionMetadata
from data_tools.services.session_history import HistoryEntry
from data_tools.services.secure_serialization import (
    SecureDataFrameSerializer, serialize_dataframe, deserialize_dataframe
)


class TestSecureSerializationSecurity(TestCase):
    """Test security aspects of the new serialization system."""
    
    def setUp(self):
        self.serializer = SecureDataFrameSerializer()
        self.test_df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e'],
            'C': [1.1, 2.2, 3.3, 4.4, 5.5],
            'D': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'])
        })
    
    def test_no_pickle_usage(self):
        """Ensure no pickle imports or usage in serialization."""
        serialized = self.serializer.serialize_dataframe(self.test_df)
        
        # Verify it's compressed JSON, not pickle
        self.assertIsInstance(serialized, bytes)
        
        # Try to deserialize back
        deserialized = self.serializer.deserialize_dataframe(serialized)
        pd.testing.assert_frame_equal(self.test_df, deserialized)
    
    def test_malicious_data_rejection(self):
        """Test that malicious serialized data is rejected."""
        # Try to deserialize random bytes (should fail safely)
        malicious_data = b"malicious_pickle_data_that_could_execute_code"
        
        with self.assertRaises(Exception):
            self.serializer.deserialize_dataframe(malicious_data)
    
    def test_data_type_preservation(self):
        """Test that all pandas data types are preserved correctly."""
        complex_df = pd.DataFrame({
            'int64': [1, 2, 3],
            'float64': [1.1, 2.2, 3.3],
            'string': ['a', 'b', 'c'],
            'datetime': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']),
            'bool': [True, False, True],
            'category': pd.Categorical(['X', 'Y', 'Z'])
        })
        
        serialized = self.serializer.serialize_dataframe(complex_df)
        deserialized = self.serializer.deserialize_dataframe(serialized)
        
        # Check data equality
        pd.testing.assert_frame_equal(complex_df, deserialized, check_dtype=False)
        
        # Verify specific types are preserved where possible
        self.assertEqual(str(deserialized['datetime'].dtype).startswith('datetime'), True)
    
    def test_compression_efficiency(self):
        """Test that compression provides reasonable space savings."""
        large_df = pd.DataFrame({
            'repeated_data': ['same_value'] * 1000,
            'sequential': list(range(1000)),
            'random': np.random.random(1000)
        })
        
        compression_ratio = self.serializer.estimate_compression_ratio(large_df)
        
        # Should achieve at least 10% compression on repetitive data
        self.assertLess(compression_ratio, 0.9)


class TestDataStudioSessionManagerCore(TestCase):
    """Test core functionality of DataStudioSessionManager."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.datasource_id = 123
        self.config = SessionConfig(timeout_minutes=60, max_history_entries=10)
        self.session_manager = DataStudioSessionManager(
            user_id=self.user.id,
            datasource_id=self.datasource_id,
            config=self.config
        )
        
        self.test_df = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': ['A', 'B', 'C', 'D', 'E'],
            'col3': [1.1, 2.2, 3.3, 4.4, 5.5]
        })
        
        # Clear cache before each test
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    def test_session_initialization(self):
        """Test successful session initialization."""
        result = self.session_manager.initialize_session(self.test_df)
        
        self.assertTrue(result)
        self.assertTrue(self.session_manager.session_exists())
        
        # Verify current DataFrame
        current_df = self.session_manager.get_current_dataframe()
        pd.testing.assert_frame_equal(self.test_df, current_df)
        
        # Verify original DataFrame
        original_df = self.session_manager.get_original_dataframe()
        pd.testing.assert_frame_equal(self.test_df, original_df)
    
    def test_prevent_duplicate_initialization(self):
        """Test that duplicate initialization is prevented."""
        # Initialize first session
        result1 = self.session_manager.initialize_session(self.test_df)
        self.assertTrue(result1)
        
        # Try to initialize again (should fail)
        result2 = self.session_manager.initialize_session(self.test_df)
        self.assertFalse(result2)
        
        # Force initialization should work
        result3 = self.session_manager.initialize_session(self.test_df, force=True)
        self.assertTrue(result3)
    
    def test_session_metadata_tracking(self):
        """Test that session metadata is properly tracked."""
        self.session_manager.initialize_session(self.test_df)
        
        session_info = self.session_manager.get_session_info()
        
        self.assertTrue(session_info['session_exists'])
        self.assertEqual(session_info['user_id'], self.user.id)
        self.assertEqual(session_info['datasource_id'], self.datasource_id)
        self.assertEqual(session_info['original_shape'], self.test_df.shape)
        self.assertEqual(session_info['current_step'], 0)
        self.assertEqual(session_info['total_operations'], 0)
        self.assertFalse(session_info['can_undo'])
        self.assertFalse(session_info['can_redo'])


class TestSessionOperations(TestCase):
    """Test session operations like apply, undo, redo."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.datasource_id = 123
        self.session_manager = DataStudioSessionManager(
            user_id=self.user.id,
            datasource_id=self.datasource_id,
            config=SessionConfig(max_history_entries=5)
        )
        
        self.original_df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e']
        })
        
        self.session_manager.initialize_session(self.original_df)
        cache.clear()  # Clear but keep session data
    
    def tearDown(self):
        cache.clear()
    
    def test_apply_transformation(self):
        """Test applying a transformation operation."""
        # Create transformed DataFrame
        transformed_df = self.original_df.copy()
        transformed_df['C'] = [6, 7, 8, 9, 10]
        
        result = self.session_manager.apply_transformation(
            transformed_df,
            'add_column',
            {'column_name': 'C', 'values': [6, 7, 8, 9, 10]}
        )
        
        self.assertTrue(result)
        
        # Check updated current DataFrame
        current_df = self.session_manager.get_current_dataframe()
        pd.testing.assert_frame_equal(transformed_df, current_df)
        
        # Check session info updated
        session_info = self.session_manager.get_session_info()
        self.assertEqual(session_info['current_step'], 1)
        self.assertEqual(session_info['total_operations'], 1)
        self.assertTrue(session_info['can_undo'])
        self.assertFalse(session_info['can_redo'])
    
    def test_undo_operation(self):
        """Test undoing an operation."""
        # Apply transformation
        transformed_df = self.original_df.copy()
        transformed_df['C'] = [6, 7, 8, 9, 10]
        self.session_manager.apply_transformation(transformed_df, 'add_column')
        
        # Undo the operation
        undone_df = self.session_manager.undo_operation()
        
        self.assertIsNotNone(undone_df)
        pd.testing.assert_frame_equal(self.original_df, undone_df)
        
        # Check session state
        session_info = self.session_manager.get_session_info()
        self.assertEqual(session_info['current_step'], 0)
        self.assertFalse(session_info['can_undo'])
        self.assertTrue(session_info['can_redo'])
    
    def test_redo_operation(self):
        """Test redoing an operation after undo."""
        # Apply transformation
        transformed_df = self.original_df.copy()
        transformed_df['C'] = [6, 7, 8, 9, 10]
        self.session_manager.apply_transformation(transformed_df, 'add_column')
        
        # Undo operation
        self.session_manager.undo_operation()
        
        # Redo operation
        redone_df = self.session_manager.redo_operation()
        
        self.assertIsNotNone(redone_df)
        
        # Check session state
        session_info = self.session_manager.get_session_info()
        self.assertEqual(session_info['current_step'], 1)
        self.assertTrue(session_info['can_undo'])
        self.assertFalse(session_info['can_redo'])
    
    def test_multiple_operations_with_undo_redo(self):
        """Test complex sequence of operations with undo/redo."""
        # Operation 1: Add column C
        df1 = self.original_df.copy()
        df1['C'] = [6, 7, 8, 9, 10]
        self.session_manager.apply_transformation(df1, 'add_column_C')
        
        # Operation 2: Add column D
        df2 = df1.copy()
        df2['D'] = [11, 12, 13, 14, 15]
        self.session_manager.apply_transformation(df2, 'add_column_D')
        
        # Operation 3: Filter rows
        df3 = df2[df2['A'] > 2].copy()
        self.session_manager.apply_transformation(df3, 'filter_rows')
        
        # Check final state
        session_info = self.session_manager.get_session_info()
        self.assertEqual(session_info['total_operations'], 3)
        self.assertEqual(session_info['current_step'], 3)
        
        # Undo twice
        self.session_manager.undo_operation()  # Back to df2
        undone_df = self.session_manager.undo_operation()  # Back to df1
        
        pd.testing.assert_frame_equal(df1, undone_df)
        
        # Redo once
        redone_df = self.session_manager.redo_operation()  # Forward to df2
        
        pd.testing.assert_frame_equal(df2, redone_df)
    
    def test_history_cleanup(self):
        """Test that old history entries are cleaned up."""
        # Apply more operations than max_history_entries
        for i in range(10):  # Config has max_history_entries=5
            df = self.original_df.copy()
            df[f'col_{i}'] = list(range(5))
            self.session_manager.apply_transformation(df, f'operation_{i}')
        
        session_info = self.session_manager.get_session_info()
        self.assertEqual(session_info['total_operations'], 10)
        
        # Should still be able to undo some operations
        undone_df = self.session_manager.undo_operation()
        self.assertIsNotNone(undone_df)


class TestSessionResetAndPause(TestCase):
    """Test session reset and pause/resume functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.datasource_id = 123
        self.session_manager = DataStudioSessionManager(
            user_id=self.user.id,
            datasource_id=self.datasource_id
        )
        
        self.original_df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e']
        })
        
        self.session_manager.initialize_session(self.original_df)
        
        # Apply some transformations
        transformed_df = self.original_df.copy()
        transformed_df['C'] = [6, 7, 8, 9, 10]
        self.session_manager.apply_transformation(transformed_df, 'add_column')
        
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    def test_reset_to_original(self):
        """Test resetting session to original state."""
        # Verify we have changes
        session_info = self.session_manager.get_session_info()
        self.assertEqual(session_info['total_operations'], 1)
        self.assertTrue(session_info['can_undo'])
        
        # Reset to original
        result = self.session_manager.reset_to_original()
        
        self.assertTrue(result)
        
        # Check that we're back to original state
        current_df = self.session_manager.get_current_dataframe()
        pd.testing.assert_frame_equal(self.original_df, current_df)
        
        # Check session state reset
        session_info = self.session_manager.get_session_info()
        self.assertEqual(session_info['current_step'], 0)
        self.assertEqual(session_info['total_operations'], 0)
        self.assertFalse(session_info['can_undo'])
        self.assertFalse(session_info['can_redo'])
    
    def test_pause_and_resume_session(self):
        """Test pausing and resuming session."""
        # Pause session
        result1 = self.session_manager.pause_session()
        self.assertTrue(result1)
        
        session_info = self.session_manager.get_session_info()
        self.assertEqual(session_info['status'], 'paused')
        
        # Resume session
        result2 = self.session_manager.resume_session()
        self.assertTrue(result2)
        
        session_info = self.session_manager.get_session_info()
        self.assertEqual(session_info['status'], 'active')
    
    def test_resume_non_paused_session_fails(self):
        """Test that resuming an active session fails."""
        # Try to resume active session
        result = self.session_manager.resume_session()
        self.assertFalse(result)


class TestSessionTimeoutAndExpiration(TestCase):
    """Test session timeout and expiration functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.datasource_id = 123
        
        # Short timeout for testing
        self.config = SessionConfig(timeout_minutes=1, cleanup_on_timeout=True)
        self.session_manager = DataStudioSessionManager(
            user_id=self.user.id,
            datasource_id=self.datasource_id,
            config=self.config
        )
        
        self.test_df = pd.DataFrame({'A': [1, 2, 3]})
        
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    @patch('pandas.Timestamp')
    def test_session_expiration_detection(self, mock_timestamp):
        """Test that expired sessions are correctly detected."""
        # Mock initial timestamp
        initial_time = pd.Timestamp('2023-01-01 12:00:00')
        mock_timestamp.now.return_value = initial_time
        
        # Initialize session
        self.session_manager.initialize_session(self.test_df)
        self.assertTrue(self.session_manager.session_exists())
        
        # Mock expired timestamp (2 minutes later, timeout is 1 minute)
        expired_time = pd.Timestamp('2023-01-01 12:02:00')
        mock_timestamp.now.return_value = expired_time
        
        # Check session existence (should clean up expired session)
        self.assertFalse(self.session_manager.session_exists())
    
    def test_session_info_includes_expiration(self):
        """Test that session info includes expiration details."""
        self.session_manager.initialize_session(self.test_df)
        
        session_info = self.session_manager.get_session_info()
        
        self.assertIn('expires_at', session_info)
        self.assertIn('is_expired', session_info)
        self.assertFalse(session_info['is_expired'])


class TestPerformanceRequirements(TestCase):
    """Test that performance requirements are met."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.datasource_id = 123
        self.session_manager = DataStudioSessionManager(
            user_id=self.user.id,
            datasource_id=self.datasource_id
        )
        
        # Create larger DataFrame for performance testing
        self.large_df = pd.DataFrame({
            'A': list(range(10000)),
            'B': ['text_' + str(i) for i in range(10000)],
            'C': np.random.random(10000),
            'D': pd.date_range('2023-01-01', periods=10000, freq='H')
        })
        
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    def test_session_initialization_performance(self):
        """Test that session initialization completes within performance requirements."""
        import time
        
        start_time = time.time()
        result = self.session_manager.initialize_session(self.large_df)
        end_time = time.time()
        
        self.assertTrue(result)
        
        # Should complete within 500ms requirement
        duration_ms = (end_time - start_time) * 1000
        self.assertLess(duration_ms, 500, f"Session initialization took {duration_ms:.2f}ms, should be < 500ms")
    
    def test_transformation_performance(self):
        """Test that transformations complete within performance requirements."""
        import time
        
        self.session_manager.initialize_session(self.large_df)
        
        # Apply transformation
        transformed_df = self.large_df.copy()
        transformed_df['E'] = transformed_df['A'] * 2
        
        start_time = time.time()
        result = self.session_manager.apply_transformation(transformed_df, 'multiply_column')
        end_time = time.time()
        
        self.assertTrue(result)
        
        # Should complete within 200ms requirement
        duration_ms = (end_time - start_time) * 1000
        self.assertLess(duration_ms, 200, f"Transformation took {duration_ms:.2f}ms, should be < 200ms")
    
    def test_undo_redo_performance(self):
        """Test that undo/redo operations complete within performance requirements."""
        import time
        
        self.session_manager.initialize_session(self.large_df)
        
        # Apply transformation
        transformed_df = self.large_df.copy()
        transformed_df['E'] = transformed_df['A'] * 2
        self.session_manager.apply_transformation(transformed_df, 'multiply_column')
        
        # Test undo performance
        start_time = time.time()
        undone_df = self.session_manager.undo_operation()
        end_time = time.time()
        
        self.assertIsNotNone(undone_df)
        
        # Should complete within 100ms requirement
        duration_ms = (end_time - start_time) * 1000
        self.assertLess(duration_ms, 100, f"Undo operation took {duration_ms:.2f}ms, should be < 100ms")
        
        # Test redo performance
        start_time = time.time()
        redone_df = self.session_manager.redo_operation()
        end_time = time.time()
        
        self.assertIsNotNone(redone_df)
        
        # Should complete within 100ms requirement
        duration_ms = (end_time - start_time) * 1000
        self.assertLess(duration_ms, 100, f"Redo operation took {duration_ms:.2f}ms, should be < 100ms")


class TestFactoryFunction(TestCase):
    """Test the factory function for creating session managers."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.datasource_id = 123
        
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    def test_factory_function(self):
        """Test that factory function creates proper session manager."""
        session_manager = get_session_manager(
            user_id=self.user.id,
            datasource_id=self.datasource_id
        )
        
        self.assertIsInstance(session_manager, DataStudioSessionManager)
        self.assertEqual(session_manager.user_id, self.user.id)
        self.assertEqual(session_manager.datasource_id, self.datasource_id)
    
    def test_factory_function_with_config(self):
        """Test factory function with custom configuration."""
        custom_config = SessionConfig(timeout_minutes=120, max_history_entries=100)
        
        session_manager = get_session_manager(
            user_id=self.user.id,
            datasource_id=self.datasource_id,
            config=custom_config
        )
        
        self.assertEqual(session_manager.config.timeout_minutes, 120)
        self.assertEqual(session_manager.config.max_history_entries, 100)


class TestIntegrationWithDjangoViews(TestCase):
    """Test integration with Django views and existing codebase."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.datasource_id = 123
        
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    def test_session_config_from_user_preferences(self):
        """Test that SessionConfig can be created from user preferences."""
        config = SessionConfig.from_user_preferences(self.user)
        
        # Should return default config for now (future enhancement)
        self.assertIsInstance(config, SessionConfig)
        self.assertEqual(config.timeout_minutes, 240)  # Default 4 hours
    
    def test_session_context_data_structure(self):
        """Test that session context data has expected structure for templates."""
        session_manager = get_session_manager(
            user_id=self.user.id,
            datasource_id=self.datasource_id
        )
        
        test_df = pd.DataFrame({'A': [1, 2, 3]})
        session_manager.initialize_session(test_df)
        
        session_info = session_manager.get_session_info()
        
        # Check required fields for template context
        required_fields = [
            'session_exists', 'user_id', 'datasource_id', 'created_at',
            'current_shape', 'original_shape', 'current_step', 'total_operations',
            'can_undo', 'can_redo', 'status'
        ]
        
        for field in required_fields:
            self.assertIn(field, session_info, f"Missing required field: {field}")
    
    def test_error_handling_in_views_context(self):
        """Test that error conditions return safe context for views."""
        # Test with non-existent session
        session_info = self.session_manager.get_session_info()
        
        self.assertEqual(session_info['session_exists'], False)
        self.assertNotIn('error', session_info)  # Should not expose internal errors