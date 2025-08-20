#!/usr/bin/env python
"""
Comprehensive Test Runner for Data Studio Components
Orchestrates the complete testing pipeline with detailed reporting
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class DataStudioTestRunner:
    """Comprehensive test runner for Data Studio components"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.test_results_dir = self.project_root / "test-results"
        self.test_results_dir.mkdir(exist_ok=True)
        
        # Test suite configuration
        self.test_suites = {
            'unit': {
                'marker': 'unit',
                'description': 'Unit tests for individual components',
                'timeout': 300,  # 5 minutes
                'parallel': True
            },
            'integration': {
                'marker': 'integration', 
                'description': 'Integration tests between components',
                'timeout': 600,  # 10 minutes
                'parallel': False
            },
            'e2e': {
                'marker': 'e2e',
                'description': 'End-to-end workflow tests',
                'timeout': 900,  # 15 minutes
                'parallel': False
            },
            'performance': {
                'marker': 'performance',
                'description': 'Performance and load tests',
                'timeout': 1200,  # 20 minutes
                'parallel': False
            },
            'websocket': {
                'marker': 'websocket',
                'description': 'WebSocket functionality tests',
                'timeout': 300,  # 5 minutes
                'parallel': False
            }
        }
        
    def run_test_suite(self, suite_name: str) -> Dict[str, Any]:
        """Run a specific test suite"""
        suite_config = self.test_suites.get(suite_name)
        if not suite_config:
            return {'success': False, 'error': f'Unknown test suite: {suite_name}'}
        
        print(f"🧪 Running {suite_config['description']}")
        print("-" * 60)
        
        start_time = time.time()
        
        # Build pytest command
        cmd = [
            'python', '-m', 'pytest',
            'data_tools/tests/',
            f"-m", suite_config['marker'],
            '--verbose',
            '--tb=short',
            f'--junit-xml={self.test_results_dir}/{suite_name}-results.xml'
        ]
        
        # Add coverage for unit and integration tests
        if suite_name in ['unit', 'integration']:
            cmd.extend([
                '--cov=data_tools',
                f'--cov-report=xml:{self.test_results_dir}/{suite_name}-coverage.xml',
                f'--cov-report=html:{self.test_results_dir}/{suite_name}-htmlcov'
            ])
        
        # Add parallel execution for unit tests
        if suite_config.get('parallel', False):
            cmd.extend(['-n', 'auto'])
        
        try:
            # Run tests with timeout
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=suite_config['timeout']
            )
            
            duration = time.time() - start_time
            
            # Parse results
            success = result.returncode == 0
            
            return {
                'suite': suite_name,
                'success': success,
                'duration': duration,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': ' '.join(cmd)
            }
            
        except subprocess.TimeoutExpired:
            return {
                'suite': suite_name,
                'success': False,
                'duration': suite_config['timeout'],
                'error': f'Test suite timed out after {suite_config["timeout"]} seconds'
            }
        except Exception as e:
            return {
                'suite': suite_name,
                'success': False,
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites and generate comprehensive report"""
        print("🚀 Starting Data Studio Comprehensive Testing")
        print("=" * 80)
        
        overall_start_time = time.time()
        suite_results = {}
        
        # Run each test suite
        for suite_name in self.test_suites.keys():
            suite_result = self.run_test_suite(suite_name)
            suite_results[suite_name] = suite_result
            
            # Display immediate results
            status = "✅ PASSED" if suite_result['success'] else "❌ FAILED"
            duration = suite_result.get('duration', 0)
            print(f"{status} {suite_name.upper()} ({duration:.1f}s)")
            
            if not suite_result['success']:
                if 'error' in suite_result:
                    print(f"   Error: {suite_result['error']}")
                elif suite_result.get('stderr'):
                    print(f"   Stderr: {suite_result['stderr'][:200]}...")
        
        overall_duration = time.time() - overall_start_time
        
        # Calculate overall statistics
        total_suites = len(suite_results)
        passed_suites = sum(1 for r in suite_results.values() if r['success'])
        failed_suites = total_suites - passed_suites
        
        # Generate comprehensive report
        report = {
            'test_run_id': f"comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'overall_duration': overall_duration,
            'summary': {
                'total_suites': total_suites,
                'passed_suites': passed_suites,
                'failed_suites': failed_suites,
                'success_rate': (passed_suites / total_suites) * 100 if total_suites > 0 else 0
            },
            'suite_results': suite_results,
            'environment': {
                'python_version': sys.version.split()[0],
                'pytest_version': self._get_pytest_version(),
                'django_version': self._get_django_version(),
                'project_root': str(self.project_root)
            }
        }
        
        # Save detailed report
        report_file = self.test_results_dir / f"comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def _get_pytest_version(self) -> str:
        """Get pytest version"""
        try:
            result = subprocess.run(['python', '-m', 'pytest', '--version'], 
                                  capture_output=True, text=True)
            return result.stdout.split()[1] if result.returncode == 0 else 'unknown'
        except:
            return 'unknown'
    
    def _get_django_version(self) -> str:
        """Get Django version"""
        try:
            import django
            return django.get_version()
        except:
            return 'unknown'
    
    def generate_test_summary(self, report: Dict[str, Any]) -> str:
        """Generate human-readable test summary"""
        summary = []
        summary.append("📋 Data Studio Testing Summary")
        summary.append("=" * 50)
        summary.append("")
        
        # Overall statistics
        summary.append(f"🕐 Total Duration: {report['overall_duration']:.1f}s")
        summary.append(f"📊 Success Rate: {report['summary']['success_rate']:.1f}%")
        summary.append(f"✅ Passed Suites: {report['summary']['passed_suites']}")
        summary.append(f"❌ Failed Suites: {report['summary']['failed_suites']}")
        summary.append("")
        
        # Suite details
        summary.append("📝 Suite Results:")
        for suite_name, result in report['suite_results'].items():
            status = "✅" if result['success'] else "❌"
            duration = result.get('duration', 0)
            description = self.test_suites[suite_name]['description']
            summary.append(f"  {status} {suite_name.upper()}: {description} ({duration:.1f}s)")
        
        summary.append("")
        
        # Environment info
        summary.append("🔧 Environment:")
        summary.append(f"  Python: {report['environment']['python_version']}")
        summary.append(f"  Pytest: {report['environment']['pytest_version']}")
        summary.append(f"  Django: {report['environment']['django_version']}")
        
        # Recommendations
        summary.append("")
        summary.append("💡 Recommendations:")
        failed_suites = [name for name, result in report['suite_results'].items() if not result['success']]
        
        if not failed_suites:
            summary.append("  🎉 All tests passed! Data Studio is ready for deployment.")
        else:
            summary.append(f"  ⚠️ {len(failed_suites)} test suite(s) failed. Review and fix before deployment:")
            for suite in failed_suites:
                summary.append(f"    • {suite}")
        
        return "\n".join(summary)
    
    def run_quick_smoke_tests(self) -> bool:
        """Run quick smoke tests to verify basic functionality"""
        print("💨 Running quick smoke tests...")
        
        cmd = [
            'python', '-m', 'pytest',
            'data_tools/tests/test_data_studio_comprehensive.py::DataStudioPaginationTestCase::test_pagination_state_management',
            'data_tools/tests/test_data_studio_comprehensive.py::DataStudioSessionTestCase::test_session_initialization',
            '-v', '--tb=line'
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, timeout=60)
            return result.returncode == 0
        except:
            return False


def main():
    """Main function for running comprehensive tests"""
    runner = DataStudioTestRunner()
    
    # Check for quick smoke test flag
    if len(sys.argv) > 1 and sys.argv[1] == '--smoke':
        success = runner.run_quick_smoke_tests()
        print(f"💨 Smoke tests: {'✅ PASSED' if success else '❌ FAILED'}")
        sys.exit(0 if success else 1)
    
    # Run comprehensive testing
    report = runner.run_all_tests()
    
    # Display summary
    print("\n" + "=" * 80)
    summary = runner.generate_test_summary(report)
    print(summary)
    
    # Save summary to file
    summary_file = runner.test_results_dir / "test_summary.md"
    with open(summary_file, 'w') as f:
        f.write(summary)
    
    print(f"\n📄 Detailed report saved to: {runner.test_results_dir}")
    
    # Exit with appropriate code
    success_rate = report['summary']['success_rate']
    sys.exit(0 if success_rate == 100 else 1)


if __name__ == "__main__":
    main()