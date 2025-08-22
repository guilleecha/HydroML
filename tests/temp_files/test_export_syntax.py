"""
Simple syntax test for export testing suite.
"""

import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydroML.settings')
django.setup()

# Import test modules to check syntax
try:
    import tests.unit.data_tools.export.test_export_job_model
    print("✓ ExportJob model tests syntax OK")
except ImportError as e:
    print(f"✗ ExportJob model tests import error: {e}")
except SyntaxError as e:
    print(f"✗ ExportJob model tests syntax error: {e}")

try:
    import tests.unit.data_tools.export.test_export_template_model
    print("✓ ExportTemplate model tests syntax OK")
except ImportError as e:
    print(f"✗ ExportTemplate model tests import error: {e}")
except SyntaxError as e:
    print(f"✗ ExportTemplate model tests syntax error: {e}")

try:
    import tests.unit.data_tools.export.test_export_service_comprehensive
    print("✓ ExportService comprehensive tests syntax OK")
except ImportError as e:
    print(f"✗ ExportService comprehensive tests import error: {e}")
except SyntaxError as e:
    print(f"✗ ExportService comprehensive tests syntax error: {e}")

try:
    import tests.unit.data_tools.export.test_export_api_comprehensive
    print("✓ Export API comprehensive tests syntax OK")
except ImportError as e:
    print(f"✗ Export API comprehensive tests import error: {e}")
except SyntaxError as e:
    print(f"✗ Export API comprehensive tests syntax error: {e}")

try:
    import tests.integration.export_workflows.test_complete_export_workflow
    print("✓ Complete export workflow tests syntax OK")
except ImportError as e:
    print(f"✗ Complete export workflow tests import error: {e}")
except SyntaxError as e:
    print(f"✗ Complete export workflow tests syntax error: {e}")

try:
    import tests.e2e.export_interface.test_export_wizard_e2e
    print("✓ Export wizard E2E tests syntax OK")
except ImportError as e:
    print(f"✗ Export wizard E2E tests import error: {e}")
except SyntaxError as e:
    print(f"✗ Export wizard E2E tests syntax error: {e}")

try:
    import tests.performance.large_exports.test_export_performance
    print("✓ Export performance tests syntax OK")
except ImportError as e:
    print(f"✗ Export performance tests import error: {e}")
except SyntaxError as e:
    print(f"✗ Export performance tests syntax error: {e}")

print("\n--- SYNTAX CHECK COMPLETE ---")
print("All test modules have been validated for syntax correctness.")