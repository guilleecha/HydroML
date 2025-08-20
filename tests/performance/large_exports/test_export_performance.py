"""
Performance tests for large export operations.

Tests performance characteristics including:
- Large dataset export performance
- Memory usage monitoring
- Concurrent export handling
- File format performance comparison
- Streaming vs batch processing
- System resource utilization
"""

import os
import time
import psutil
import tempfile
import pandas as pd
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from data_tools.models.export_job import ExportJob
from data_tools.services.export_service import ExportService
from projects.models.project import Project
from projects.models.datasource import DataSource

User = get_user_model()


class ExportPerformanceTestCase(TestCase):
    """Base class for export performance tests."""
    
    def setUp(self):
        """Set up test data and performance monitoring."""
        self.user = User.objects.create_user(
            username='perfuser',
            email='perf@example.com',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            name='Performance Test Project',
            user=self.user
        )
        self.project.members.add(self.user)
        
        self.export_service = ExportService()
        
        # Performance tracking
        self.process = psutil.Process()
        self.start_memory = self.process.memory_info().rss
        self.start_time = time.time()

    def create_large_dataset(self, num_rows=100000):
        """Create a large test dataset."""
        # Generate realistic test data
        data = {
            'id': range(1, num_rows + 1),
            'name': [f'User_{i}' for i in range(1, num_rows + 1)],
            'email': [f'user_{i}@example.com' for i in range(1, num_rows + 1)],
            'age': [(20 + i % 50) for i in range(num_rows)],
            'department': [f'Dept_{i % 10}' for i in range(num_rows)],
            'salary': [(50000 + (i * 100) % 100000) for i in range(num_rows)],
            'active': [(i % 2 == 0) for i in range(num_rows)],
            'created_at': [timezone.now().isoformat() for _ in range(num_rows)]
        }
        
        df = pd.DataFrame(data)
        
        # Save to temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            csv_path = f.name
        
        # Create DataSource
        with open(csv_path, 'rb') as f:
            csv_content = f.read()
        
        csv_file = SimpleUploadedFile(
            f"large_dataset_{num_rows}.csv",
            csv_content,
            content_type="text/csv"
        )
        
        datasource = DataSource.objects.create(
            name=f'Large Dataset ({num_rows} rows)',
            file=csv_file,
            format='csv',
            user=self.user,
            status=DataSource.Status.READY
        )
        datasource.projects.add(self.project)
        
        # Clean up temporary file
        os.unlink(csv_path)
        
        return datasource

    def measure_performance(self, func, *args, **kwargs):
        """Measure performance of a function execution."""
        start_time = time.time()
        start_memory = self.process.memory_info().rss
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = self.process.memory_info().rss
        
        return {
            'result': result,
            'duration': end_time - start_time,
            'memory_delta': end_memory - start_memory,
            'peak_memory': end_memory
        }

    def assertPerformanceWithin(self, metrics, max_duration=None, max_memory_mb=None):
        """Assert that performance metrics are within acceptable limits."""
        if max_duration:
            self.assertLess(
                metrics['duration'], 
                max_duration,
                f"Operation took {metrics['duration']:.2f}s, expected < {max_duration}s"
            )
        
        if max_memory_mb:
            memory_mb = metrics['memory_delta'] / (1024 * 1024)
            self.assertLess(
                memory_mb,
                max_memory_mb,
                f"Memory usage was {memory_mb:.2f}MB, expected < {max_memory_mb}MB"
            )


class LargeDatasetExportPerformanceTest(ExportPerformanceTestCase):
    """Test export performance with large datasets."""

    def test_100k_rows_csv_export_performance(self):
        """Test CSV export performance with 100K rows."""
        datasource = self.create_large_dataset(100000)
        
        def export_operation():
            job = self.export_service.create_export_job(
                user=self.user,
                datasource_id=datasource.id,
                export_format='csv'
            )
            success = self.export_service.process_export(str(job.id))
            return job, success
        
        metrics = self.measure_performance(export_operation)
        
        job, success = metrics['result']
        self.assertTrue(success)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'completed')
        self.assertEqual(job.row_count, 100000)
        
        # Performance assertions - adjust based on system requirements
        self.assertPerformanceWithin(
            metrics,
            max_duration=30.0,      # 30 seconds max
            max_memory_mb=500       # 500MB max memory increase
        )
        
        # File should be reasonable size
        self.assertGreater(job.file_size, 1000000)   # At least 1MB
        self.assertLess(job.file_size, 50000000)     # Less than 50MB
        
        # Cleanup
        if job.file_path and os.path.exists(job.file_path):
            os.unlink(job.file_path)

    def test_format_performance_comparison(self):
        """Compare performance across different export formats."""
        datasource = self.create_large_dataset(50000)  # Smaller dataset for format comparison
        
        formats = ['csv', 'json', 'parquet']
        results = {}
        
        for format_type in formats:
            def export_operation():
                job = self.export_service.create_export_job(
                    user=self.user,
                    datasource_id=datasource.id,
                    export_format=format_type
                )
                success = self.export_service.process_export(str(job.id))
                return job, success
            
            metrics = self.measure_performance(export_operation)
            job, success = metrics['result']
            
            self.assertTrue(success, f"{format_type} export failed")
            
            job.refresh_from_db()
            results[format_type] = {
                'duration': metrics['duration'],
                'memory_delta': metrics['memory_delta'],
                'file_size': job.file_size
            }
            
            # Cleanup
            if job.file_path and os.path.exists(job.file_path):
                os.unlink(job.file_path)
        
        # Performance comparisons
        # CSV should be fastest for writing
        self.assertLess(
            results['csv']['duration'],
            results['json']['duration'],
            "CSV should be faster than JSON"
        )
        
        # Parquet should have smallest file size (most compressed)
        self.assertLess(
            results['parquet']['file_size'],
            results['csv']['file_size'],
            "Parquet should be more compressed than CSV"
        )
        
        # Print results for analysis
        for format_type, metrics in results.items():
            print(f"{format_type.upper()}: "
                  f"Duration: {metrics['duration']:.2f}s, "
                  f"Memory: {metrics['memory_delta'] / (1024*1024):.2f}MB, "
                  f"File Size: {metrics['file_size'] / (1024*1024):.2f}MB")

    def test_memory_usage_large_export(self):
        """Test memory consumption during large exports."""
        datasource = self.create_large_dataset(200000)  # 200K rows
        
        # Monitor memory during export
        memory_samples = []
        monitoring = True
        
        def memory_monitor():
            while monitoring:
                memory_samples.append(self.process.memory_info().rss)
                time.sleep(0.1)  # Sample every 100ms
        
        # Start memory monitoring
        monitor_thread = Thread(target=memory_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            # Perform export
            job = self.export_service.create_export_job(
                user=self.user,
                datasource_id=datasource.id,
                export_format='csv'
            )
            
            success = self.export_service.process_export(str(job.id))
            self.assertTrue(success)
            
        finally:
            # Stop monitoring
            monitoring = False
            monitor_thread.join(timeout=1)
        
        # Analyze memory usage
        if memory_samples:
            base_memory = memory_samples[0]
            peak_memory = max(memory_samples)
            memory_delta = peak_memory - base_memory
            
            # Memory should not increase by more than 1GB
            self.assertLess(
                memory_delta / (1024 * 1024 * 1024),
                1.0,
                f"Memory increased by {memory_delta / (1024*1024):.2f}MB"
            )
        
        # Cleanup
        job.refresh_from_db()
        if job.file_path and os.path.exists(job.file_path):
            os.unlink(job.file_path)

    def test_filtered_export_performance(self):
        """Test performance of exports with filters applied."""
        datasource = self.create_large_dataset(100000)
        
        # Test different filter scenarios
        filter_scenarios = [
            {'columns': ['id', 'name', 'email']},  # Column filter
            {'limit': 50000},                      # Row limit
            {'columns': ['name', 'department'], 'limit': 25000},  # Combined
        ]
        
        for i, filters in enumerate(filter_scenarios):
            def export_operation():
                job = self.export_service.create_export_job(
                    user=self.user,
                    datasource_id=datasource.id,
                    export_format='csv',
                    filters=filters
                )
                success = self.export_service.process_export(str(job.id))
                return job, success
            
            metrics = self.measure_performance(export_operation)
            job, success = metrics['result']
            
            self.assertTrue(success, f"Filtered export {i} failed")
            
            job.refresh_from_db()
            
            # Filtered exports should be faster and use less memory
            self.assertPerformanceWithin(
                metrics,
                max_duration=20.0,      # Should be faster than full export
                max_memory_mb=300       # Should use less memory
            )
            
            # Verify filter was applied
            if 'limit' in filters:
                self.assertLessEqual(job.row_count, filters['limit'])
            
            # Cleanup
            if job.file_path and os.path.exists(job.file_path):
                os.unlink(job.file_path)


class ConcurrentExportPerformanceTest(TransactionTestCase):
    """Test performance with concurrent export operations."""

    def setUp(self):
        """Set up test data for concurrent operations."""
        super().setUp()
        
        self.user = User.objects.create_user(
            username='concurrentuser',
            email='concurrent@example.com',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            name='Concurrent Test Project',
            user=self.user
        )
        self.project.members.add(self.user)
        
        # Create multiple datasources for concurrent testing
        self.datasources = []
        for i in range(5):
            datasource = self.create_small_dataset(f'Dataset_{i}', 10000)
            self.datasources.append(datasource)
        
        self.export_service = ExportService()

    def create_small_dataset(self, name, num_rows=10000):
        """Create a smaller dataset for concurrent testing."""
        data = {
            'id': range(1, num_rows + 1),
            'name': [f'User_{i}' for i in range(num_rows)],
            'value': [i * 2 for i in range(num_rows)]
        }
        
        df = pd.DataFrame(data)
        csv_content = df.to_csv(index=False).encode()
        
        csv_file = SimpleUploadedFile(
            f"{name}.csv",
            csv_content,
            content_type="text/csv"
        )
        
        datasource = DataSource.objects.create(
            name=name,
            file=csv_file,
            format='csv',
            user=self.user,
            status=DataSource.Status.READY
        )
        datasource.projects.add(self.project)
        
        return datasource

    def test_concurrent_export_jobs(self):
        """Test system performance with multiple concurrent exports."""
        def export_worker(datasource):
            """Worker function for concurrent export."""
            start_time = time.time()
            
            job = self.export_service.create_export_job(
                user=self.user,
                datasource_id=datasource.id,
                export_format='csv'
            )
            
            success = self.export_service.process_export(str(job.id))
            
            end_time = time.time()
            
            return {
                'job': job,
                'success': success,
                'duration': end_time - start_time,
                'datasource_name': datasource.name
            }
        
        # Execute exports concurrently
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(export_worker, datasource)
                for datasource in self.datasources
            ]
            
            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        total_time = time.time() - start_time
        
        # All exports should succeed
        for result in results:
            self.assertTrue(result['success'], 
                          f"Export for {result['datasource_name']} failed")
            
            job = result['job']
            job.refresh_from_db()
            self.assertEqual(job.status, 'completed')
        
        # Concurrent execution should be faster than sequential
        # (assuming sufficient system resources)
        max_single_duration = max(result['duration'] for result in results)
        self.assertLess(
            total_time,
            max_single_duration * 5,  # Should be less than 5x single job
            "Concurrent execution not providing performance benefit"
        )
        
        # Average individual job time should be reasonable
        avg_job_time = sum(result['duration'] for result in results) / len(results)
        self.assertLess(avg_job_time, 10.0, "Individual jobs taking too long")
        
        # Cleanup
        for result in results:
            job = result['job']
            if job.file_path and os.path.exists(job.file_path):
                os.unlink(job.file_path)

    def test_resource_contention_handling(self):
        """Test handling of resource contention under load."""
        # Create many concurrent export requests
        num_concurrent = 10
        
        def create_export_job(i):
            datasource = self.datasources[i % len(self.datasources)]
            return self.export_service.create_export_job(
                user=self.user,
                datasource_id=datasource.id,
                export_format='json'
            )
        
        # Create multiple jobs quickly
        start_time = time.time()
        jobs = []
        
        for i in range(num_concurrent):
            job = create_export_job(i)
            jobs.append(job)
        
        creation_time = time.time() - start_time
        
        # Job creation should be fast even under contention
        self.assertLess(creation_time, 5.0, "Job creation too slow under load")
        
        # Process jobs and measure system behavior
        def process_job(job):
            start_time = time.time()
            success = self.export_service.process_export(str(job.id))
            duration = time.time() - start_time
            return success, duration
        
        process_start = time.time()
        
        with ThreadPoolExecutor(max_workers=3) as executor:  # Limited workers
            futures = [executor.submit(process_job, job) for job in jobs]
            processing_results = [future.result() for future in futures]
        
        total_processing_time = time.time() - process_start
        
        # All jobs should complete successfully despite contention
        successful_jobs = sum(1 for success, _ in processing_results if success)
        self.assertEqual(successful_jobs, num_concurrent)
        
        # System should handle contention gracefully
        self.assertLess(
            total_processing_time,
            60.0,  # Should complete within 1 minute
            "System not handling resource contention well"
        )
        
        # Cleanup
        for job in jobs:
            job.refresh_from_db()
            if job.file_path and os.path.exists(job.file_path):
                os.unlink(job.file_path)


class ExportScalabilityTest(ExportPerformanceTestCase):
    """Test export scalability with varying dataset sizes."""

    def test_scalability_across_dataset_sizes(self):
        """Test how export performance scales with dataset size."""
        sizes = [1000, 10000, 50000, 100000]  # Progressive sizes
        results = {}
        
        for size in sizes:
            datasource = self.create_large_dataset(size)
            
            def export_operation():
                job = self.export_service.create_export_job(
                    user=self.user,
                    datasource_id=datasource.id,
                    export_format='csv'
                )
                success = self.export_service.process_export(str(job.id))
                return job, success
            
            metrics = self.measure_performance(export_operation)
            job, success = metrics['result']
            
            self.assertTrue(success, f"Export of {size} rows failed")
            
            job.refresh_from_db()
            results[size] = {
                'duration': metrics['duration'],
                'memory_delta': metrics['memory_delta'],
                'file_size': job.file_size,
                'throughput': size / metrics['duration']  # rows per second
            }
            
            # Cleanup
            if job.file_path and os.path.exists(job.file_path):
                os.unlink(job.file_path)
        
        # Analyze scalability characteristics
        sizes_list = sorted(results.keys())
        
        for i in range(1, len(sizes_list)):
            current_size = sizes_list[i]
            prev_size = sizes_list[i-1]
            
            size_ratio = current_size / prev_size
            time_ratio = results[current_size]['duration'] / results[prev_size]['duration']
            
            # Time should scale sub-linearly (better than O(n))
            self.assertLess(
                time_ratio,
                size_ratio * 1.5,  # Allow some overhead
                f"Poor scalability from {prev_size} to {current_size} rows"
            )
        
        # Print scalability analysis
        print("\nScalability Analysis:")
        print("Size\t\tDuration\tThroughput\tMemory")
        for size in sizes_list:
            r = results[size]
            print(f"{size:,}\t\t{r['duration']:.2f}s\t\t"
                  f"{r['throughput']:.0f} rows/s\t{r['memory_delta']/(1024*1024):.1f}MB")

    def test_file_size_optimization(self):
        """Test file size optimization across different scenarios."""
        datasource = self.create_large_dataset(50000)
        
        # Test different optimization scenarios
        scenarios = [
            {
                'name': 'Full Export',
                'format': 'csv',
                'filters': {},
                'options': {}
            },
            {
                'name': 'Compressed CSV',
                'format': 'csv',
                'filters': {},
                'options': {'compression': True}
            },
            {
                'name': 'Column Subset',
                'format': 'csv',
                'filters': {'columns': ['id', 'name']},
                'options': {}
            },
            {
                'name': 'Parquet Compressed',
                'format': 'parquet',
                'filters': {},
                'options': {'compression': 'snappy'}
            }
        ]
        
        results = {}
        
        for scenario in scenarios:
            job = self.export_service.create_export_job(
                user=self.user,
                datasource_id=datasource.id,
                export_format=scenario['format'],
                filters=scenario['filters'],
                options=scenario['options']
            )
            
            success = self.export_service.process_export(str(job.id))
            self.assertTrue(success, f"Scenario '{scenario['name']}' failed")
            
            job.refresh_from_db()
            results[scenario['name']] = {
                'file_size': job.file_size,
                'row_count': job.row_count
            }
            
            # Cleanup
            if job.file_path and os.path.exists(job.file_path):
                os.unlink(job.file_path)
        
        # File size optimizations should work
        full_export_size = results['Full Export']['file_size']
        
        # Column subset should be smaller
        if 'Column Subset' in results:
            self.assertLess(
                results['Column Subset']['file_size'],
                full_export_size,
                "Column subset should reduce file size"
            )
        
        # Parquet should be more compressed
        if 'Parquet Compressed' in results:
            self.assertLess(
                results['Parquet Compressed']['file_size'],
                full_export_size,
                "Parquet should be more compressed"
            )
        
        # Print optimization results
        print("\nFile Size Optimization Results:")
        for name, result in results.items():
            size_mb = result['file_size'] / (1024 * 1024)
            print(f"{name}: {size_mb:.2f}MB ({result['row_count']} rows)")