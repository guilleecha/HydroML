#!/usr/bin/env python
"""
Pre-Test Environment Validation Script
Validates that the HydroML environment is ready for QA testing
"""

import requests
import time
import subprocess
import sys

def check_docker_containers():
    """Check if all required Docker containers are running"""
    print("🔍 Checking Docker containers...")
    
    try:
        result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Failed to run docker-compose ps")
            return False
        
        output = result.stdout
        required_services = ['web', 'db', 'redis', 'mlflow', 'worker']
        
        for service in required_services:
            if service in output and 'Up' in output:
                print(f"✅ {service} container is running")
            else:
                print(f"❌ {service} container is not running")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error checking containers: {e}")
        return False

def check_web_accessibility():
    """Check if the web application is accessible"""
    print("\n🌐 Checking web application accessibility...")
    
    try:
        response = requests.get('http://localhost:8000', timeout=10)
        if response.status_code == 200:
            print("✅ Web application is accessible at http://localhost:8000")
            return True
        else:
            print(f"❌ Web application returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to web application at http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error accessing web application: {e}")
        return False

def check_mlflow_accessibility():
    """Check if MLflow server is accessible"""
    print("\n🧪 Checking MLflow server accessibility...")
    
    try:
        response = requests.get('http://localhost:5000', timeout=10)
        if response.status_code == 200:
            print("✅ MLflow server is accessible at http://localhost:5000")
            return True
        else:
            print(f"❌ MLflow server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to MLflow server at http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error accessing MLflow server: {e}")
        return False

def check_database_connectivity():
    """Check if the database is accessible via Django"""
    print("\n🗄️ Checking database connectivity...")
    
    try:
        result = subprocess.run([
            'docker-compose', 'exec', '-T', 'web', 
            'python', 'manage.py', 'check', '--database', 'default'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database connectivity is working")
            return True
        else:
            print(f"❌ Database check failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def create_test_data():
    """Create sample test data if needed"""
    print("\n📊 Creating test CSV file for upload testing...")
    
    test_csv_content = """name,age,salary,department,years_experience
John Doe,25,50000,Engineering,3
Jane Smith,30,65000,Marketing,5
Bob Johnson,35,75000,Engineering,8
Alice Brown,28,55000,Sales,4
Charlie Wilson,32,70000,Engineering,6
Diana Davis,29,58000,Marketing,3
Eve Thompson,31,72000,Sales,7
Frank Miller,27,52000,Engineering,2
"""
    
    try:
        with open('test_data.csv', 'w') as f:
            f.write(test_csv_content)
        print("✅ Test CSV file created: test_data.csv")
        return True
    except Exception as e:
        print(f"❌ Failed to create test CSV: {e}")
        return False

def main():
    """Main validation function"""
    print("🧪 HydroML QA Environment Validation")
    print("=" * 50)
    
    validation_results = []
    
    # Check Docker containers
    validation_results.append(check_docker_containers())
    
    # Wait a moment for services to be fully ready
    print("\n⏳ Waiting for services to be fully ready...")
    time.sleep(3)
    
    # Check web application
    validation_results.append(check_web_accessibility())
    
    # Check MLflow server
    validation_results.append(check_mlflow_accessibility())
    
    # Check database connectivity
    validation_results.append(check_database_connectivity())
    
    # Create test data
    validation_results.append(create_test_data())
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = sum(validation_results)
    total = len(validation_results)
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Environment is ready for QA testing")
        print("\n📋 Next Steps:")
        print("   1. Open your browser and navigate to http://localhost:8000")
        print("   2. Login with your test credentials")
        print("   3. Begin executing the test cases from the QA Test Plan")
        print("   4. Use test_data.csv for datasource upload testing")
        return True
    else:
        print(f"❌ {total - passed} checks failed out of {total}")
        print("🚨 Environment is NOT ready for QA testing")
        print("\n🔧 Troubleshooting:")
        print("   1. Run: docker-compose down && docker-compose up -d")
        print("   2. Wait 2-3 minutes for all services to start")
        print("   3. Run this validation script again")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
