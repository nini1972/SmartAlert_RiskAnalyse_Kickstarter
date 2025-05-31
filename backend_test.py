
import requests
import json
import unittest
from datetime import datetime, timedelta
import time

class KickstarterAPITester(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = "https://d2b4b685-66a1-4946-9970-01e9da7727d3.preview.emergentagent.com/api"
        self.project_id = None
        self.investment_id = None

    def test_01_api_root(self):
        """Test API root endpoint"""
        print("\n🔍 Testing API root endpoint...")
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        print("✅ API root endpoint test passed")

    def test_02_create_project(self):
        """Test creating a new project"""
        print("\n🔍 Testing project creation...")
        
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
        self.assertEqual(response.status_code, 200)
        
        # Verify response contains expected fields
        project = response.json()
        self.assertIn("id", project)
        self.assertEqual(project["name"], project_data["name"])
        self.assertEqual(project["creator"], project_data["creator"])
        self.assertEqual(project["category"], project_data["category"])
        
        # Verify AI analysis was performed
        self.assertIn("ai_analysis", project)
        self.assertIn("risk_level", project)
        
        # Store project ID for later tests
        self.__class__.project_id = project["id"]
        print(f"✅ Project creation test passed (ID: {self.project_id})")

    def test_03_get_projects(self):
        """Test getting all projects"""
        print("\n🔍 Testing get all projects...")
        response = requests.get(f"{self.base_url}/projects")
        self.assertEqual(response.status_code, 200)
        
        projects = response.json()
        self.assertIsInstance(projects, list)
        
        # Verify our created project is in the list
        project_ids = [p["id"] for p in projects]
        self.assertIn(self.project_id, project_ids)
        print("✅ Get all projects test passed")

    def test_04_get_project_by_id(self):
        """Test getting a specific project by ID"""
        print("\n🔍 Testing get project by ID...")
        response = requests.get(f"{self.base_url}/projects/{self.project_id}")
        self.assertEqual(response.status_code, 200)
        
        project = response.json()
        self.assertEqual(project["id"], self.project_id)
        print("✅ Get project by ID test passed")

    def test_05_create_investment(self):
        """Test creating a new investment"""
        print("\n🔍 Testing investment creation...")
        
        investment_data = {
            "project_id": self.project_id,
            "amount": 100.0,
            "investment_date": datetime.now().isoformat(),
            "expected_return": 120.0,
            "notes": "Test investment",
            "reward_tier": "Basic Tier"
        }
        
        response = requests.post(f"{self.base_url}/investments", json=investment_data)
        self.assertEqual(response.status_code, 200)
        
        investment = response.json()
        self.assertIn("id", investment)
        self.assertEqual(investment["project_id"], self.project_id)
        self.assertEqual(investment["amount"], investment_data["amount"])
        
        # Store investment ID for later tests
        self.__class__.investment_id = investment["id"]
        print(f"✅ Investment creation test passed (ID: {self.investment_id})")

    def test_06_get_investments(self):
        """Test getting all investments"""
        print("\n🔍 Testing get all investments...")
        response = requests.get(f"{self.base_url}/investments")
        self.assertEqual(response.status_code, 200)
        
        investments = response.json()
        self.assertIsInstance(investments, list)
        
        # Verify our created investment is in the list
        if self.investment_id:
            investment_ids = [i["id"] for i in investments]
            self.assertIn(self.investment_id, investment_ids)
        print("✅ Get all investments test passed")

    def test_07_get_investments_by_project(self):
        """Test getting investments for a specific project"""
        print("\n🔍 Testing get investments by project ID...")
        response = requests.get(f"{self.base_url}/investments?project_id={self.project_id}")
        self.assertEqual(response.status_code, 200)
        
        investments = response.json()
        self.assertIsInstance(investments, list)
        
        # Verify all returned investments are for our project
        for investment in investments:
            self.assertEqual(investment["project_id"], self.project_id)
        print("✅ Get investments by project ID test passed")

    def test_08_get_dashboard_stats(self):
        """Test getting dashboard statistics"""
        print("\n🔍 Testing dashboard statistics...")
        response = requests.get(f"{self.base_url}/dashboard/stats")
        self.assertEqual(response.status_code, 200)
        
        stats = response.json()
        self.assertIn("total_projects", stats)
        self.assertIn("total_investments", stats)
        self.assertIn("total_invested", stats)
        self.assertIn("risk_distribution", stats)
        self.assertIn("category_distribution", stats)
        print("✅ Dashboard statistics test passed")

    def test_09_get_ai_recommendations(self):
        """Test getting AI recommendations"""
        print("\n🔍 Testing AI recommendations...")
        response = requests.get(f"{self.base_url}/recommendations")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("recommendations", data)
        self.assertIsInstance(data["recommendations"], list)
        print("✅ AI recommendations test passed")

    def test_10_update_project(self):
        """Test updating a project"""
        print("\n🔍 Testing project update...")
        
        # Get current project data
        response = requests.get(f"{self.base_url}/projects/{self.project_id}")
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
        self.assertEqual(response.status_code, 200)
        
        updated_project = response.json()
        self.assertEqual(updated_project["id"], self.project_id)
        self.assertEqual(updated_project["name"], update_data["name"])
        self.assertEqual(updated_project["status"], update_data["status"])
        self.assertEqual(updated_project["pledged_amount"], update_data["pledged_amount"])
        
        # Verify AI analysis was updated
        self.assertIn("ai_analysis", updated_project)
        print("✅ Project update test passed")

    def test_11_delete_project(self):
        """Test deleting a project"""
        print("\n🔍 Testing project deletion...")
        
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
        temp_project_id = response.json()["id"]
        
        # Delete the project
        response = requests.delete(f"{self.base_url}/projects/{temp_project_id}")
        self.assertEqual(response.status_code, 200)
        
        # Verify project is deleted
        response = requests.get(f"{self.base_url}/projects/{temp_project_id}")
        self.assertEqual(response.status_code, 404)
        print("✅ Project deletion test passed")

    def test_12_error_handling(self):
        """Test error handling for invalid requests"""
        print("\n🔍 Testing error handling...")
        
        # Test invalid project ID
        response = requests.get(f"{self.base_url}/projects/invalid-id")
        self.assertEqual(response.status_code, 404)
        
        # Test invalid investment creation (missing required fields)
        invalid_investment = {
            "amount": 100.0  # Missing project_id and investment_date
        }
        response = requests.post(f"{self.base_url}/investments", json=invalid_investment)
        self.assertNotEqual(response.status_code, 200)
        
        print("✅ Error handling test passed")

if __name__ == "__main__":
    # Run tests in order
    test_suite = unittest.TestSuite()
    test_suite.addTest(KickstarterAPITester('test_01_api_root'))
    test_suite.addTest(KickstarterAPITester('test_02_create_project'))
    test_suite.addTest(KickstarterAPITester('test_03_get_projects'))
    test_suite.addTest(KickstarterAPITester('test_04_get_project_by_id'))
    test_suite.addTest(KickstarterAPITester('test_05_create_investment'))
    test_suite.addTest(KickstarterAPITester('test_06_get_investments'))
    test_suite.addTest(KickstarterAPITester('test_07_get_investments_by_project'))
    test_suite.addTest(KickstarterAPITester('test_08_get_dashboard_stats'))
    test_suite.addTest(KickstarterAPITester('test_09_get_ai_recommendations'))
    test_suite.addTest(KickstarterAPITester('test_10_update_project'))
    test_suite.addTest(KickstarterAPITester('test_11_delete_project'))
    test_suite.addTest(KickstarterAPITester('test_12_error_handling'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)
