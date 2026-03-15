import os
import pathlib
from typing import Dict, Any
from ..templates.rf_templates import RFTemplates

class TestAgent:
    def __init__(self):
        self.rf_templates = RFTemplates()
        self.projects_folder = "rf_projects"
        
    async def handle_create_test(self, user_message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle test case creation requests"""
        test_name = entities.get("test_name", "sample_test")
        test_description = entities.get("test_description", "Basic test case")
        test_suite = entities.get("test_suite", "custom_tests")
        
        # Clean test name
        test_name = self._clean_test_name(test_name)
        
        message = f"""I'll create a new Robot Framework test case:

**Test Name:** {test_name}
**Description:** {test_description}
**Test Suite:** {test_suite}.robot

The test will include:
- Test case structure with keywords
- Basic setup and teardown
- Sample test steps
- Documentation

Shall I create this test case?"""
        
        return {
            "message": message,
            "requires_confirmation": True,
            "action": {
                "type": "create_test",
                "test_name": test_name,
                "test_description": test_description,
                "test_suite": test_suite
            }
        }
    
    async def create_test_case(self, test_name: str, test_description: str, test_suite: str = "custom_tests") -> Dict[str, Any]:
        """Actually create the test case file"""
        try:
            # Find existing project or create in default location
            projects_path = pathlib.Path(self.projects_folder)
            
            # Look for existing projects
            project_folders = [p for p in projects_path.iterdir() if p.is_dir()] if projects_path.exists() else []
            
            if project_folders:
                # Use the most recent project
                project_path = max(project_folders, key=os.path.getctime)
            else:
                # Create a default project
                project_path = projects_path / "default_project"
                project_path.mkdir(parents=True, exist_ok=True)
                (project_path / "tests").mkdir(exist_ok=True)
                (project_path / "resources").mkdir(exist_ok=True)
            
            tests_path = project_path / "tests"
            test_file_path = tests_path / f"{test_suite}.robot"
            
            # Generate test content
            test_content = self.rf_templates.get_test_case_template(
                test_name=test_name,
                test_description=test_description,
                test_suite=test_suite
            )
            
            # Write the test file
            with open(test_file_path, "w") as f:
                f.write(test_content)
            
            return {
                "success": True,
                "message": f"✅ Test case '{test_name}' created successfully!\n\nFile: {test_file_path.absolute()}\n\nThe test is ready to run with: robot {test_file_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error creating test case: {str(e)}"
            }
    
    async def add_test_to_existing_suite(self, test_name: str, test_description: str, suite_file: str) -> Dict[str, Any]:
        """Add a test case to an existing test suite"""
        try:
            suite_path = pathlib.Path(suite_file)
            
            if not suite_path.exists():
                return {
                    "success": False,
                    "message": f"❌ Test suite file not found: {suite_file}"
                }
            
            # Read existing content
            with open(suite_path, "r") as f:
                existing_content = f.read()
            
            # Generate new test case
            new_test = self.rf_templates.get_single_test_case(test_name, test_description)
            
            # Append to existing file
            updated_content = existing_content + "\n" + new_test
            
            with open(suite_path, "w") as f:
                f.write(updated_content)
            
            return {
                "success": True,
                "message": f"✅ Test case '{test_name}' added to {suite_path.name}!"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error adding test case: {str(e)}"
            }
    
    def _clean_test_name(self, name: str) -> str:
        """Clean test name to be Robot Framework compatible"""
        # Replace spaces with underscores and keep it readable
        cleaned = " ".join(word.capitalize() for word in name.split())
        return cleaned 