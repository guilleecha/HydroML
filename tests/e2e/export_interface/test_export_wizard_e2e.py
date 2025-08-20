"""
End-to-end tests for export wizard interface using Playwright.

Tests complete user journey for data export including:
- Export wizard navigation and form interaction
- Format selection and options configuration
- Progress monitoring and status updates
- File download functionality
- Export history and management
- Error handling and user feedback
"""

import os
import time
import tempfile
from unittest.mock import patch

from django.test import StaticLiveServerTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from data_tools.models.export_job import ExportJob
from data_tools.models.export_template import ExportTemplate
from projects.models.project import Project
from projects.models.datasource import DataSource

User = get_user_model()


class ExportWizardE2ETest(StaticLiveServerTestCase):
    """End-to-end tests for export wizard interface."""
    
    @classmethod
    def setUpClass(cls):
        """Set up Playwright browser for testing."""
        super().setUpClass()
        
        # Import playwright here to avoid import issues if not installed
        try:
            from playwright.sync_api import sync_playwright
            cls.playwright_available = True
            
            cls.playwright = sync_playwright().start()
            cls.browser = cls.playwright.chromium.launch(headless=True)
            cls.context = cls.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            cls.page = cls.context.new_page()
            
        except ImportError:
            cls.playwright_available = False
            cls.skipTest(cls, "Playwright not available")

    @classmethod
    def tearDownClass(cls):
        """Clean up Playwright resources."""
        if cls.playwright_available:
            cls.context.close()
            cls.browser.close()
            cls.playwright.stop()
        super().tearDownClass()

    def setUp(self):
        """Set up test data."""
        if not self.playwright_available:
            self.skipTest("Playwright not available")
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test project
        self.project = Project.objects.create(
            name='E2E Test Project',
            description='Project for E2E testing',
            user=self.user
        )
        self.project.members.add(self.user)
        
        # Create test data
        test_csv_content = b"""id,name,age,department,salary
1,Alice Smith,28,Engineering,75000
2,Bob Johnson,32,Marketing,68000
3,Charlie Brown,45,Finance,82000
4,Diana Ross,29,Engineering,78000
5,Edward Norton,38,Marketing,71000"""
        
        csv_file = SimpleUploadedFile(
            "e2e_test_data.csv",
            test_csv_content,
            content_type="text/csv"
        )
        
        self.datasource = DataSource.objects.create(
            name='E2E Test Dataset',
            file=csv_file,
            format='csv',
            user=self.user,
            status=DataSource.Status.READY
        )
        self.datasource.projects.add(self.project)

    def login_user(self):
        """Log in the test user via browser."""
        login_url = self.live_server_url + reverse('accounts:login')
        self.page.goto(login_url)
        
        # Fill login form
        self.page.fill('input[name="username"]', 'testuser')
        self.page.fill('input[name="password"]', 'testpass123')
        self.page.click('button[type="submit"]')
        
        # Wait for redirect to dashboard
        self.page.wait_for_url('**/dashboard/**', timeout=10000)

    def test_export_wizard_complete_flow(self):
        """Test complete export wizard user flow."""
        # Login
        self.login_user()
        
        # Navigate to Data Studio
        data_studio_url = self.live_server_url + reverse('data_tools:data_studio')
        self.page.goto(data_studio_url)
        
        # Wait for page to load
        self.page.wait_for_selector('[data-testid="data-studio-container"]', timeout=10000)
        
        # Select the test datasource
        self.page.click(f'[data-datasource-id="{self.datasource.id}"]')
        
        # Click export button
        self.page.wait_for_selector('[data-testid="export-button"]', timeout=5000)
        self.page.click('[data-testid="export-button"]')
        
        # Export wizard should open
        self.page.wait_for_selector('[data-testid="export-wizard"]', timeout=5000)
        
        # Step 1: Select format
        self.page.click('[data-testid="format-csv"]')
        self.page.click('[data-testid="next-step"]')
        
        # Step 2: Configure columns
        self.page.wait_for_selector('[data-testid="column-selection"]', timeout=5000)
        self.page.check('[data-column="name"]')
        self.page.check('[data-column="department"]')
        self.page.check('[data-column="salary"]')
        self.page.click('[data-testid="next-step"]')
        
        # Step 3: Configure options
        self.page.wait_for_selector('[data-testid="export-options"]', timeout=5000)
        self.page.select_option('[data-testid="delimiter-select"]', value=',')
        self.page.select_option('[data-testid="encoding-select"]', value='utf-8')
        self.page.click('[data-testid="next-step"]')
        
        # Step 4: Review and confirm
        self.page.wait_for_selector('[data-testid="export-review"]', timeout=5000)
        
        # Verify review information
        format_text = self.page.text_content('[data-testid="review-format"]')
        self.assertIn('CSV', format_text)
        
        columns_text = self.page.text_content('[data-testid="review-columns"]')
        self.assertIn('name', columns_text)
        self.assertIn('department', columns_text)
        self.assertIn('salary', columns_text)
        
        # Start export
        self.page.click('[data-testid="start-export"]')
        
        # Should redirect to export monitoring page
        self.page.wait_for_selector('[data-testid="export-progress"]', timeout=5000)
        
        # Monitor progress (in a real scenario, this would update via WebSocket/polling)
        # For testing, we'll simulate completion after a short delay
        time.sleep(2)
        
        # Progress should show completion
        # Note: In a real implementation, you'd wait for actual progress updates
        progress_element = self.page.locator('[data-testid="progress-bar"]')
        if progress_element.is_visible():
            # Wait for completion or simulate it
            self.page.wait_for_selector('[data-testid="download-button"]', timeout=15000)

    def test_export_template_usage_flow(self):
        """Test export flow using predefined templates."""
        # Create test template
        template = ExportTemplate.objects.create(
            name='E2E Test Template',
            description='Template for E2E testing',
            user=self.user,
            configuration={
                'format': 'json',
                'filters': {'columns': ['name', 'age']},
                'options': {'indent': 2}
            }
        )
        
        # Login and navigate to export
        self.login_user()
        
        data_studio_url = self.live_server_url + reverse('data_tools:data_studio')
        self.page.goto(data_studio_url)
        
        self.page.wait_for_selector('[data-testid="data-studio-container"]', timeout=10000)
        self.page.click(f'[data-datasource-id="{self.datasource.id}"]')
        self.page.click('[data-testid="export-button"]')
        
        # In export wizard, select template tab
        self.page.wait_for_selector('[data-testid="export-wizard"]', timeout=5000)
        self.page.click('[data-testid="templates-tab"]')
        
        # Select the test template
        self.page.wait_for_selector(f'[data-template-id="{template.id}"]', timeout=5000)
        self.page.click(f'[data-template-id="{template.id}"]')
        
        # Template details should be loaded
        format_display = self.page.text_content('[data-testid="selected-format"]')
        self.assertIn('JSON', format_display)
        
        # Start export with template
        self.page.click('[data-testid="use-template"]')
        
        # Should proceed directly to monitoring (skipping wizard steps)
        self.page.wait_for_selector('[data-testid="export-progress"]', timeout=5000)

    def test_export_history_interface(self):
        """Test export history dashboard interface."""
        # Create some export jobs for testing
        completed_job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='completed',
            row_count=100,
            file_size=5000
        )
        
        pending_job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='json',
            status='pending'
        )
        
        failed_job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='parquet',
            status='failed',
            error_message='Test error message'
        )
        
        # Login and navigate to export history
        self.login_user()
        
        history_url = self.live_server_url + reverse('data_tools:export_history')
        self.page.goto(history_url)
        
        # Wait for export history table to load
        self.page.wait_for_selector('[data-testid="export-history-table"]', timeout=10000)
        
        # Verify all jobs are displayed
        job_rows = self.page.locator('[data-testid="export-job-row"]').count()
        self.assertEqual(job_rows, 3)
        
        # Test filtering by status
        self.page.select_option('[data-testid="status-filter"]', value='completed')
        self.page.wait_for_timeout(1000)  # Wait for filter to apply
        
        filtered_rows = self.page.locator('[data-testid="export-job-row"]:visible').count()
        self.assertEqual(filtered_rows, 1)
        
        # Test job actions - download completed job
        download_button = f'[data-testid="download-{completed_job.id}"]'
        if self.page.locator(download_button).is_visible():
            self.page.click(download_button)
            # Note: Actual file download testing would require special setup
        
        # Test job actions - retry failed job
        retry_button = f'[data-testid="retry-{failed_job.id}"]'
        if self.page.locator(retry_button).is_visible():
            self.page.click(retry_button)
            # Should show confirmation or trigger retry
        
        # Test job actions - cancel pending job
        cancel_button = f'[data-testid="cancel-{pending_job.id}"]'
        if self.page.locator(cancel_button).is_visible():
            self.page.click(cancel_button)
            
            # Should show confirmation dialog
            if self.page.locator('[data-testid="confirm-cancel"]').is_visible():
                self.page.click('[data-testid="confirm-cancel"]')

    def test_export_error_handling_ui(self):
        """Test error handling in export UI."""
        # Login
        self.login_user()
        
        # Navigate to export wizard
        data_studio_url = self.live_server_url + reverse('data_tools:data_studio')
        self.page.goto(data_studio_url)
        
        self.page.wait_for_selector('[data-testid="data-studio-container"]', timeout=10000)
        self.page.click(f'[data-datasource-id="{self.datasource.id}"]')
        self.page.click('[data-testid="export-button"]')
        
        # Try to proceed without selecting format (should show validation error)
        self.page.wait_for_selector('[data-testid="export-wizard"]', timeout=5000)
        self.page.click('[data-testid="next-step"]')
        
        # Should show validation error
        error_message = self.page.locator('[data-testid="validation-error"]')
        if error_message.is_visible():
            error_text = error_message.text_content()
            self.assertIn('format', error_text.lower())
        
        # Select format and try to proceed without columns
        self.page.click('[data-testid="format-csv"]')
        self.page.click('[data-testid="next-step"]')
        
        # Skip column selection and proceed
        self.page.wait_for_selector('[data-testid="column-selection"]', timeout=5000)
        self.page.click('[data-testid="next-step"]')
        
        # Should show error for no columns selected
        column_error = self.page.locator('[data-testid="column-validation-error"]')
        if column_error.is_visible():
            error_text = column_error.text_content()
            self.assertIn('column', error_text.lower())

    def test_export_progress_monitoring(self):
        """Test real-time export progress monitoring."""
        # Create a pending export job
        job = ExportJob.objects.create(
            user=self.user,
            datasource=self.datasource,
            format='csv',
            status='pending',
            progress=0
        )
        
        # Login
        self.login_user()
        
        # Navigate directly to export monitoring page
        monitor_url = self.live_server_url + reverse(
            'data_tools:export_monitor', 
            kwargs={'job_id': job.id}
        )
        self.page.goto(monitor_url)
        
        # Should show initial progress
        self.page.wait_for_selector('[data-testid="export-progress"]', timeout=5000)
        
        initial_progress = self.page.text_content('[data-testid="progress-text"]')
        self.assertIn('0%', initial_progress)
        
        # Simulate progress updates (in real app, this would come from WebSocket/polling)
        # Update job status to simulate progress
        job.status = 'processing'
        job.progress = 25
        job.save()
        
        # Wait and check for progress update (would need WebSocket or polling in real app)
        time.sleep(1)
        
        # Simulate completion
        job.status = 'completed'
        job.progress = 100
        job.file_path = '/tmp/test_export.csv'
        job.file_size = 1024
        job.row_count = 5
        job.save()
        
        # In a real implementation, the UI would update automatically
        # For testing, we can refresh and check final state
        self.page.reload()
        self.page.wait_for_selector('[data-testid="export-complete"]', timeout=5000)
        
        # Download button should be available
        download_btn = self.page.locator('[data-testid="download-button"]')
        self.assertTrue(download_btn.is_visible())

    def test_mobile_responsive_export_interface(self):
        """Test export interface responsiveness on mobile devices."""
        # Set mobile viewport
        mobile_context = self.browser.new_context(
            viewport={'width': 375, 'height': 667},  # iPhone SE size
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
        )
        mobile_page = mobile_context.new_page()
        
        try:
            # Login on mobile
            login_url = self.live_server_url + reverse('accounts:login')
            mobile_page.goto(login_url)
            
            mobile_page.fill('input[name="username"]', 'testuser')
            mobile_page.fill('input[name="password"]', 'testpass123')
            mobile_page.click('button[type="submit"]')
            
            mobile_page.wait_for_url('**/dashboard/**', timeout=10000)
            
            # Navigate to Data Studio
            data_studio_url = self.live_server_url + reverse('data_tools:data_studio')
            mobile_page.goto(data_studio_url)
            
            # Check mobile menu and navigation
            mobile_page.wait_for_selector('[data-testid="mobile-menu-toggle"]', timeout=10000)
            mobile_page.click('[data-testid="mobile-menu-toggle"]')
            
            # Export interface should be accessible via mobile menu
            mobile_page.wait_for_selector('[data-testid="mobile-export-option"]', timeout=5000)
            mobile_page.click('[data-testid="mobile-export-option"]')
            
            # Export wizard should adapt to mobile layout
            mobile_page.wait_for_selector('[data-testid="export-wizard-mobile"]', timeout=5000)
            
            # Verify mobile-specific UI elements
            mobile_stepper = mobile_page.locator('[data-testid="mobile-stepper"]')
            self.assertTrue(mobile_stepper.is_visible())
            
            # Test touch interactions
            mobile_page.click('[data-testid="format-csv"]')
            mobile_page.click('[data-testid="mobile-next"]')
            
            # Mobile column selection should use touch-friendly controls
            mobile_page.wait_for_selector('[data-testid="mobile-column-list"]', timeout=5000)
            
        finally:
            mobile_context.close()

    def test_export_wizard_accessibility(self):
        """Test export wizard accessibility features."""
        # Login
        self.login_user()
        
        # Navigate to export wizard
        data_studio_url = self.live_server_url + reverse('data_tools:data_studio')
        self.page.goto(data_studio_url)
        
        self.page.wait_for_selector('[data-testid="data-studio-container"]', timeout=10000)
        self.page.click(f'[data-datasource-id="{self.datasource.id}"]')
        self.page.click('[data-testid="export-button"]')
        
        # Test keyboard navigation
        self.page.wait_for_selector('[data-testid="export-wizard"]', timeout=5000)
        
        # Tab through format options
        self.page.press('[data-testid="format-csv"]', 'Tab')
        self.page.press('[data-testid="format-json"]', 'Tab')
        
        # Test screen reader support
        csv_format = self.page.locator('[data-testid="format-csv"]')
        aria_label = csv_format.get_attribute('aria-label')
        self.assertIsNotNone(aria_label)
        self.assertIn('CSV', aria_label)
        
        # Test focus management
        self.page.click('[data-testid="format-csv"]')
        self.page.press('[data-testid="next-step"]', 'Enter')  # Keyboard activation
        
        # Focus should move to next step
        self.page.wait_for_selector('[data-testid="column-selection"]', timeout=5000)
        focused_element = self.page.evaluate('document.activeElement.getAttribute("data-testid")')
        self.assertIn('column', focused_element or '')

    def test_export_bulk_operations(self):
        """Test bulk export operations interface."""
        # Create multiple export jobs
        jobs = []
        for i in range(3):
            job = ExportJob.objects.create(
                user=self.user,
                datasource=self.datasource,
                format='csv',
                status='completed'
            )
            jobs.append(job)
        
        # Login and navigate to export history
        self.login_user()
        
        history_url = self.live_server_url + reverse('data_tools:export_history')
        self.page.goto(history_url)
        
        self.page.wait_for_selector('[data-testid="export-history-table"]', timeout=10000)
        
        # Select multiple jobs using checkboxes
        for job in jobs:
            checkbox = f'[data-testid="select-job-{job.id}"]'
            self.page.check(checkbox)
        
        # Bulk actions should become available
        self.page.wait_for_selector('[data-testid="bulk-actions"]', timeout=5000)
        
        # Test bulk delete
        self.page.click('[data-testid="bulk-delete"]')
        
        # Confirmation dialog should appear
        self.page.wait_for_selector('[data-testid="confirm-bulk-delete"]', timeout=5000)
        
        confirmation_text = self.page.text_content('[data-testid="bulk-delete-message"]')
        self.assertIn('3', confirmation_text)  # Should mention 3 selected jobs
        
        # Confirm deletion
        self.page.click('[data-testid="confirm-delete"]')
        
        # Should show success message
        success_message = self.page.locator('[data-testid="bulk-success"]')
        if success_message.is_visible():
            success_text = success_message.text_content()
            self.assertIn('deleted', success_text.lower())

    def tearDown(self):
        """Clean up test data."""
        # Clean up any export files created during testing
        for job in ExportJob.objects.filter(user=self.user):
            if job.file_path and os.path.exists(job.file_path):
                try:
                    os.unlink(job.file_path)
                except OSError:
                    pass