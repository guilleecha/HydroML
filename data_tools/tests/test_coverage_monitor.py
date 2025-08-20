"""
Test Coverage Monitor
Provides utilities for monitoring and reporting test coverage across Data Studio components
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class TestCoverageMonitor:
    """Monitor and report test coverage statistics"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.coverage_file = self.project_root / "coverage.xml"
        self.reports_dir = self.project_root / "test-reports"
        self.reports_dir.mkdir(exist_ok=True)
        
    def parse_coverage_xml(self) -> Dict[str, Any]:
        """Parse coverage.xml file and extract coverage statistics"""
        if not self.coverage_file.exists():
            return self._default_coverage_stats()
            
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(self.coverage_file)
            root = tree.getroot()
            
            # Extract overall coverage
            overall_line_rate = float(root.get('line-rate', 0)) * 100
            overall_branch_rate = float(root.get('branch-rate', 0)) * 100
            
            # Extract package coverage
            packages = {}
            for package in root.findall('.//package'):
                name = package.get('name', 'unknown')
                line_rate = float(package.get('line-rate', 0)) * 100
                branch_rate = float(package.get('branch-rate', 0)) * 100
                
                packages[name] = {
                    'line_coverage': line_rate,
                    'branch_coverage': branch_rate
                }
            
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_line_coverage': overall_line_rate,
                'overall_branch_coverage': overall_branch_rate,
                'package_coverage': packages,
                'meets_threshold': overall_line_coverage >= 90.0
            }
            
        except Exception as e:
            print(f"Error parsing coverage.xml: {e}")
            return self._default_coverage_stats()
    
    def _default_coverage_stats(self) -> Dict[str, Any]:
        """Return default coverage statistics when coverage.xml is not available"""
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_line_coverage': 0.0,
            'overall_branch_coverage': 0.0,
            'package_coverage': {},
            'meets_threshold': False,
            'error': 'Coverage file not found'
        }
    
    def generate_coverage_report(self) -> Dict[str, Any]:
        """Generate comprehensive coverage report"""
        coverage_stats = self.parse_coverage_xml()
        
        # Component-specific coverage targets
        component_targets = {
            'data_tools.services': 95.0,
            'data_tools.views': 90.0,
            'data_tools.websockets': 85.0,
            'data_tools.static.data_tools.js': 80.0  # JavaScript coverage (estimated)
        }
        
        # Analyze component coverage
        component_analysis = {}
        for component, target in component_targets.items():
            package_coverage = coverage_stats['package_coverage'].get(component, {'line_coverage': 0.0})
            actual_coverage = package_coverage['line_coverage']
            
            component_analysis[component] = {
                'actual_coverage': actual_coverage,
                'target_coverage': target,
                'meets_target': actual_coverage >= target,
                'gap': max(0, target - actual_coverage)
            }
        
        report = {
            'report_id': f"coverage_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'generated_at': datetime.now().isoformat(),
            'overall_stats': coverage_stats,
            'component_analysis': component_analysis,
            'quality_gates': {
                'overall_threshold': 90.0,
                'component_threshold': 85.0,
                'critical_components': ['data_tools.services', 'data_tools.views']
            },
            'recommendations': self._generate_recommendations(component_analysis)
        }
        
        # Save report
        report_file = self.reports_dir / f"coverage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def _generate_recommendations(self, component_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on coverage analysis"""
        recommendations = []
        
        for component, stats in component_analysis.items():
            if not stats['meets_target']:
                gap = stats['gap']
                if gap > 10:
                    recommendations.append(f"CRITICAL: {component} needs {gap:.1f}% more coverage")
                elif gap > 5:
                    recommendations.append(f"HIGH: {component} needs {gap:.1f}% more coverage")
                else:
                    recommendations.append(f"MEDIUM: {component} needs {gap:.1f}% more coverage")
        
        if not recommendations:
            recommendations.append("✅ All components meet coverage targets")
        
        return recommendations
    
    def create_coverage_badge(self, coverage_percentage: float) -> str:
        """Create a coverage badge SVG"""
        color = self._get_coverage_color(coverage_percentage)
        
        badge_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="104" height="20">
            <linearGradient id="b" x2="0" y2="100%">
                <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
                <stop offset="1" stop-opacity=".1"/>
            </linearGradient>
            <clipPath id="a">
                <rect width="104" height="20" rx="3" fill="#fff"/>
            </clipPath>
            <g clip-path="url(#a)">
                <path fill="#555" d="M0 0h63v20H0z"/>
                <path fill="{color}" d="M63 0h41v20H63z"/>
                <path fill="url(#b)" d="M0 0h104v20H0z"/>
            </g>
            <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110">
                <text x="325" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="530">coverage</text>
                <text x="325" y="140" transform="scale(.1)" textLength="530">coverage</text>
                <text x="835" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="310">{coverage_percentage:.0f}%</text>
                <text x="835" y="140" transform="scale(.1)" textLength="310">{coverage_percentage:.0f}%</text>
            </g>
        </svg>'''
        
        return badge_svg
    
    def _get_coverage_color(self, percentage: float) -> str:
        """Get color based on coverage percentage"""
        if percentage >= 95:
            return "#4c1"  # Bright green
        elif percentage >= 90:
            return "#97ca00"  # Green
        elif percentage >= 80:
            return "#a4a61d"  # Yellow-green
        elif percentage >= 70:
            return "#dfb317"  # Yellow
        elif percentage >= 60:
            return "#fe7d37"  # Orange
        else:
            return "#e05d44"  # Red
    
    def monitor_coverage_trends(self) -> Dict[str, Any]:
        """Monitor coverage trends over time"""
        trend_file = self.reports_dir / "coverage_trends.json"
        
        current_stats = self.parse_coverage_xml()
        
        # Load existing trends
        trends = []
        if trend_file.exists():
            try:
                with open(trend_file, 'r') as f:
                    trends = json.load(f)
            except:
                trends = []
        
        # Add current measurement
        trends.append({
            'timestamp': current_stats['timestamp'],
            'line_coverage': current_stats['overall_line_coverage'],
            'branch_coverage': current_stats['overall_branch_coverage']
        })
        
        # Keep only last 30 measurements
        trends = trends[-30:]
        
        # Save updated trends
        with open(trend_file, 'w') as f:
            json.dump(trends, f, indent=2)
        
        # Calculate trend analysis
        if len(trends) >= 2:
            recent_coverage = trends[-1]['line_coverage']
            previous_coverage = trends[-2]['line_coverage']
            trend_direction = "increasing" if recent_coverage > previous_coverage else "decreasing"
            trend_change = abs(recent_coverage - previous_coverage)
        else:
            trend_direction = "stable"
            trend_change = 0.0
        
        return {
            'current_coverage': current_stats['overall_line_coverage'],
            'trend_direction': trend_direction,
            'trend_change': trend_change,
            'measurements_count': len(trends),
            'historical_data': trends
        }


def main():
    """Main function for running coverage monitoring"""
    monitor = TestCoverageMonitor()
    
    print("🔍 Generating Data Studio Test Coverage Report")
    print("=" * 60)
    
    # Generate coverage report
    report = monitor.generate_coverage_report()
    
    # Display summary
    print(f"Overall Line Coverage: {report['overall_stats']['overall_line_coverage']:.1f}%")
    print(f"Overall Branch Coverage: {report['overall_stats']['overall_branch_coverage']:.1f}%")
    print(f"Meets Threshold (90%): {'✅' if report['overall_stats']['meets_threshold'] else '❌'}")
    
    # Display component analysis
    print("\nComponent Coverage Analysis:")
    for component, stats in report['component_analysis'].items():
        status = "✅" if stats['meets_target'] else "❌"
        print(f"  {status} {component}: {stats['actual_coverage']:.1f}% (target: {stats['target_coverage']:.1f}%)")
    
    # Display recommendations
    print("\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    
    # Monitor trends
    trends = monitor.monitor_coverage_trends()
    print(f"\nCoverage Trend: {trends['trend_direction'].upper()}")
    if trends['trend_change'] > 0:
        print(f"Change: {trends['trend_change']:.1f}%")
    
    # Create coverage badge
    coverage_percentage = report['overall_stats']['overall_line_coverage']
    badge_svg = monitor.create_coverage_badge(coverage_percentage)
    
    badge_file = monitor.reports_dir / "coverage-badge.svg"
    with open(badge_file, 'w') as f:
        f.write(badge_svg)
    
    print(f"\n📊 Coverage report saved to: {monitor.reports_dir}")
    print(f"🏆 Coverage badge saved to: {badge_file}")


if __name__ == "__main__":
    main()