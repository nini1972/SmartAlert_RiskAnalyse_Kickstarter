
import requests
import json
from datetime import datetime, timedelta
import sys

class KickstarterAPITester:
    def __init__(self):
        self.base_url = "https://d2b4b685-66a1-4946-9970-01e9da7727d3.preview.emergentagent.com/api"
        self.project_id = None
        self.investment_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0

    def run_test(self, name, test_func):
        """Run a single test with proper error handling"""
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            result = test_func()
            if result:
                self.tests_passed += 1
                print(f"✅ {name} test passed")
                return True
            else:
                self.tests_failed += 1
                print(f"❌ {name} test failed")
                return False
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ {name} test failed with error: {str(e)}")
            return False

    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{self.base_url}/")
        if response.status_code != 200:
            print(f"  Error: Expected status 200, got {response.status_code}")
            return False
        
        data = response.json()
        if "message" not in data:
            print("  Error: Response missing 'message' field")
            return False
            
        return True

    def test_create_project(self):
        """Test creating a new project"""
        # Create test project data
        deadline = (datetime.now() + timedelta(days=30)).isoformat()
        launched_date = (datetime.now() - timedelta(days=5)).isoformat()
        
        project_data = {
            "name": "Test AI Robot Assistant",
            "creator": "Test Creator",
            "url": "https://www.kickstarter.com/projects/test/test-project",
            "description": "A revolutionary AI-powered robot assistant for testing purposes",
            "category": "Technology",
            "goal_amount": 50000,
            "pledged_amount": 25000,
            "backers_count": 150,
            "deadline": deadline,
            "launched_date": launched_date,
            "status": "live"
        }
        
        response = requests.post(f"{self.base_url}/projects", json=project_data)
        if response.status_code != 200:
            print(f"  Error: Expected status 200, got {response.status_code}")
            print(f"  Response: {response.text}")
            return False
        
        # Verify response contains expected fields
        project = response.json()
        if "id" not in project:
            print("  Error: Response missing 'id' field")
            return False
            
        if project["name"] != project_data["name"]:
            print(f"  Error: Expected name '{project_data['name']}', got '{project['name']}'")
            return False
            
        if "ai_analysis" not in project:
            print("  Error: Response missing 'ai_analysis' field")
            return False
            
        # Store project ID for later tests
        self.project_id = project["id"]
        print(f"  Created project with ID: {self.project_id}")
        return True

    def test_get_projects(self):
        """Test getting all projects"""
        if not self.project_id:
            print("  Error: No project ID available from previous test")
            return False
            
        response = requests.get(f"{self.base_url}/projects")
        if response.status_code != 200:
            print(f"  Error: Expected status 200, got {response.status_code}")
            return False
        
        projects = response.json()
        if not isinstance(projects, list):
            print(f"  Error: Expected list response, got {type(projects)}")
            return False
            
        # Verify our created project is in the list
        project_ids = [p["id"] for p in projects]
        if self.project_id not in project_ids:
            print(f"  Error: Created project ID {self.project_id} not found in projects list")
            return False
            
        return True

    def test_get_project_by_id(self):
        """Test getting a specific project by ID"""
        if not self.project_id:
            print("  Error: No project ID available from previous test")
            return False
            
        response = requests.get(f"{self.base_url}/projects/{self.project_id}")
        if response.status_code != 200:
            print(f"  Error: Expected status 200, got {response.status_code}")
            return False
        
        project = response.json()
        if project["id"] != self.project_id:
            print(f"  Error: Expected project ID {self.project_id}, got {project['id']}")
            return False
            
        return True

    def test_create_investment(self):
        """Test creating a new investment"""
        if not self.project_id:
            print("  Error: No project ID available from previous test")
            return False
            
        investment_data = {
            "project_id": self.project_id,
            "amount": 100.0,
            "investment_date": datetime.now().isoformat(),
            "expected_return": 120.0,
            "notes": "Test investment",
            "reward_tier": "Basic Tier"
        }
        
        response = requests.post(f"{self.base_url}/investments", json=investment_data)
        if response.status_code != 200:
            print(f"  Error: Expected status 200, got {response.status_code}")
            print(f"  Response: {response.text}")
            return False
        
        investment = response.json()
        if "id" not in investment:
            print("  Error: Response missing 'id' field")
            return False
            
        if investment["project_id"] != self.project_id:
            print(f"  Error: Expected project_id {self.project_id}, got {investment['project_id']}")
            return False
            
        # Store investment ID for later tests
        self.investment_id = investment["id"]
        print(f"  Created investment with ID: {self.investment_id}")
        return True

    def test_get_investments(self):
        """Test getting all investments"""
        response = requests.get(f"{self.base_url}/investments")
        if response.status_code != 200:
            print(f"  Error: Expected status 200, got {response.status_code}")
            return False
        
        investments = response.json()
        if not isinstance(investments, list):
            print(f"  Error: Expected list response, got {type(investments)}")
            return False
            
        # If we have an investment ID, verify it's in the list
        if self.investment_id:
            investment_ids = [i["id"] for i in investments]
            if self.investment_id not in investment_ids:
                print(f"  Error: Created investment ID {self.investment_id} not found in investments list")
                return False
                
        return True

    def test_get_investments_by_project(self):
        """Test getting investments for a specific project"""
        if not self.project_id:
            print("  Error: No project ID available from previous test")
            return False
            
        response = requests.get(f"{self.base_url}/investments?project_id={self.project_id}")
        if response.status_code != 200:
            print(f"  Error: Expected status 200, got {response.status_code}")
            return False
        
        investments = response.json()
        if not isinstance(investments, list):
            print(f"  Error: Expected list response, got {type(investments)}")
            return False
            
        # Verify all returned investments are for our project
        for investment in investments:
            if investment["project_id"] != self.project_id:
                print(f"  Error: Found investment with project_id {investment['project_id']}, expected {self.project_id}")
                return False
                
        return True

    def test_dashboard_stats(self):
        """Test getting dashboard statistics"""
        response = requests.get(f"{self.base_url}/dashboard/stats")
        if response.status_code != 200:
            print(f"  Error: Expected status 200, got {response.status_code}")
            return False
        
        stats = response.json()
        required_fields = ["total_projects", "total_investments", "total_invested", 
                          "risk_distribution", "category_distribution"]
                          
        for field in required_fields:
            if field not in stats:
                print(f"  Error: Response missing '{field}' field")
                return False
                
        return True

    def test_ai_recommendations(self):
        """Test getting AI recommendations"""
        response = requests.get(f"{self.base_url}/recommendations")
        if response.status_code != 200:
            print(f"  Error: Expected status 200, got {response.status_code}")
            return False
        
        data = response.json()
        if "recommendations" not in data:
            print("  Error: Response missing 'recommendations' field")
            return False
            
        if not isinstance(data["recommendations"], list):
            print(f"  Error: Expected 'recommendations' to be a list, got {type(data['recommendations'])}")
            return False
            
        return True

    def test_update_project(self):
        """Test updating a project"""
        if not self.project_id:
            print("  Error: No project ID available from previous test")
            return False
            
        # Get current project data
        response = requests.get(f"{self.base_url}/projects/{self.project_id}")
        if response.status_code != 200:
            print(f"  Error: Failed to get current project data, status {response.status_code}")
            return False
            
        current_project = response.json()
        
        # Update some fields
        update_data = {
            "name": current_project["name"] + " (Updated)",
            "creator": current_project["creator"],
            "url": current_project["url"],
            "description": current_project["description"] + " This project has been updated.",
            "category": current_project["category"],
            "goal_amount": float(current_project["goal_amount"]),
            "pledged_amount": float(current_project["pledged_amount"]) + 5000,
            "backers_count": current_project["backers_count"] + 50,
            "deadline": current_project["deadline"],
            "launched_date": current_project["launched_date"],
            "status": "successful"  # Change status
        }
        
        response = requests.put(f"{self.base_url}/projects/{self.project_id}", json=update_data)
        if response.status_code != 200:
            print(f"  Error: Expected status 200, got {response.status_code}")
            print(f"  Response: {response.text}")
            return False
        
        updated_project = response.json()
        if updated_project["id"] != self.project_id:
            print(f"  Error: Expected project ID {self.project_id}, got {updated_project['id']}")
            return False
            
        if updated_project["name"] != update_data["name"]:
            print(f"  Error: Expected name '{update_data['name']}', got '{updated_project['name']}'")
            return False
            
        if updated_project["status"] != update_data["status"]:
            print(f"  Error: Expected status '{update_data['status']}', got '{updated_project['status']}'")
            return False
            
        if "ai_analysis" not in updated_project:
            print("  Error: Response missing 'ai_analysis' field")
            return False
            
        return True

    def test_delete_project(self):
        """Test deleting a project"""
        # Create a temporary project to delete
        deadline = (datetime.now() + timedelta(days=30)).isoformat()
        launched_date = (datetime.now() - timedelta(days=5)).isoformat()
        
        project_data = {
            "name": "Temporary Project to Delete",
            "creator": "Test Creator",
            "url": "https://www.kickstarter.com/projects/test/temp-project",
            "description": "This project will be deleted",
            "category": "Technology",
            "goal_amount": 10000,
            "pledged_amount": 0,
            "backers_count": 0,
            "deadline": deadline,
            "launched_date": launched_date,
            "status": "live"
        }
        
        response = requests.post(f"{self.base_url}/projects", json=project_data)
        if response.status_code != 200:
            print(f"  Error: Failed to create temporary project, status {response.status_code}")
            return False
            
        temp_project_id = response.json()["id"]
        print(f"  Created temporary project with ID: {temp_project_id}")
        
        # Delete the project
        response = requests.delete(f"{self.base_url}/projects/{temp_project_id}")
        if response.status_code != 200:
            print(f"  Error: Expected status 200 for delete, got {response.status_code}")
            return False
        
        # Verify project is deleted
        response = requests.get(f"{self.base_url}/projects/{temp_project_id}")
        if response.status_code != 404:
            print(f"  Error: Expected status 404 after deletion, got {response.status_code}")
            return False
            
        return True

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        # Test invalid project ID
        response = requests.get(f"{self.base_url}/projects/invalid-id")
        if response.status_code != 404:
            print(f"  Error: Expected status 404 for invalid project ID, got {response.status_code}")
            return False
        
        # Test invalid investment creation (missing required fields)
        invalid_investment = {
            "amount": 100.0  # Missing project_id and investment_date
        }
        response = requests.post(f"{self.base_url}/investments", json=invalid_investment)
        if response.status_code == 200:
            print("  Error: Expected non-200 status for invalid investment data, got 200")
            return False
            
        return True

    def test_smart_alerts(self):
        """Test getting smart alerts"""
        response = requests.get(f"{self.base_url}/alerts")
        if response.status_code != 200:
            print(f"  Error: Expected status 200, got {response.status_code}")
            return False
        
        alerts = response.json()
        if not isinstance(alerts, list):
            print(f"  Error: Expected list response, got {type(alerts)}")
            return False
            
        # Check alert structure if any alerts exist
        if alerts:
            required_fields = ["id", "project_id", "alert_type", "message", "priority", "is_read", "created_at"]
            for field in required_fields:
                if field not in alerts[0]:
                    print(f"  Error: Alert missing '{field}' field")
                    return False
                    
            # Verify priority values are valid
            valid_priorities = ["high", "medium", "low"]
            for alert in alerts:
                if alert["priority"] not in valid_priorities:
                    print(f"  Error: Invalid priority '{alert['priority']}' in alert")
                    return False
        
        print(f"  Found {len(alerts)} alerts")
        return True
        
    def test_alert_settings(self):
        """Test getting and updating alert settings"""
        # Get current settings
        response = requests.get(f"{self.base_url}/alerts/settings")
        if response.status_code != 200:
            print(f"  Error: Expected status 200, got {response.status_code}")
            return False
        
        settings = response.json()
        required_fields = ["notification_frequency", "min_funding_velocity", "preferred_categories", 
                          "max_risk_level", "min_success_probability", "browser_notifications"]
                          
        for field in required_fields:
            if field not in settings:
                print(f"  Error: Settings missing '{field}' field")
                return False
        
        # Update settings
        updated_settings = settings.copy()
        updated_settings["notification_frequency"] = "daily"
        updated_settings["min_funding_velocity"] = 0.2
        updated_settings["max_risk_level"] = "high"
        
        response = requests.post(f"{self.base_url}/alerts/settings", json=updated_settings)
        if response.status_code != 200:
            print(f"  Error: Expected status 200 for settings update, got {response.status_code}")
            print(f"  Response: {response.text}")
            return False
        
        # Verify settings were updated
        response = requests.get(f"{self.base_url}/alerts/settings")
        if response.status_code != 200:
            print(f"  Error: Failed to get updated settings, status {response.status_code}")
            return False
            
        new_settings = response.json()
        if new_settings["notification_frequency"] != updated_settings["notification_frequency"]:
            print(f"  Error: Setting not updated correctly. Expected '{updated_settings['notification_frequency']}', got '{new_settings['notification_frequency']}'")
            return False
            
        return True
        
    def test_advanced_analytics(self):
        """Test getting advanced analytics"""
        response = requests.get(f"{self.base_url}/analytics/advanced")
        if response.status_code != 200:
            print(f"  Error: Expected status 200, got {response.status_code}")
            return False
        
        analytics = response.json()
        required_fields = ["roi_prediction", "funding_velocity", "market_sentiment", 
                          "diversification_score", "risk_adjusted_return", "recommended_actions"]
                          
        for field in required_fields:
            if field not in analytics:
                print(f"  Error: Analytics missing '{field}' field")
                return False
                
        if not isinstance(analytics["recommended_actions"], list):
            print(f"  Error: Expected 'recommended_actions' to be a list, got {type(analytics['recommended_actions'])}")
            return False
            
        return True
        
    def test_funding_trends(self):
        """Test getting funding trends data"""
        response = requests.get(f"{self.base_url}/analytics/funding-trends")
        if response.status_code != 200:
            print(f"  Error: Expected status 200, got {response.status_code}")
            return False
        
        data = response.json()
        if "trends" not in data:
            print("  Error: Response missing 'trends' field")
            return False
            
        if not isinstance(data["trends"], list):
            print(f"  Error: Expected 'trends' to be a list, got {type(data['trends'])}")
            return False
            
        # Check trend data structure if any trends exist
        if data["trends"]:
            required_fields = ["name", "velocity", "success_probability", "pledged_percentage", "risk_level", "category"]
            for field in required_fields:
                if field not in data["trends"][0]:
                    print(f"  Error: Trend data missing '{field}' field")
                    return False
        
        print(f"  Found {len(data['trends'])} trend entries")
        return True
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        tests = [
            ("API Root", self.test_api_root),
            ("Create Project", self.test_create_project),
            ("Get Projects", self.test_get_projects),
            ("Get Project by ID", self.test_get_project_by_id),
            ("Create Investment", self.test_create_investment),
            ("Get Investments", self.test_get_investments),
            ("Get Investments by Project", self.test_get_investments_by_project),
            ("Dashboard Statistics", self.test_dashboard_stats),
            ("AI Recommendations", self.test_ai_recommendations),
            ("Smart Alerts", self.test_smart_alerts),
            ("Alert Settings", self.test_alert_settings),
            ("Advanced Analytics", self.test_advanced_analytics),
            ("Funding Trends", self.test_funding_trends),
            ("Update Project", self.test_update_project),
            ("Delete Project", self.test_delete_project),
            ("Error Handling", self.test_error_handling)
        ]
        
        for name, test_func in tests:
            self.run_test(name, test_func)
            
        # Print summary
        print("\n📊 Test Summary:")
        print(f"  Total tests: {self.tests_run}")
        print(f"  Passed: {self.tests_passed}")
        print(f"  Failed: {self.tests_failed}")
        
        return self.tests_failed == 0

if __name__ == "__main__":
    tester = KickstarterAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
