import os
import pathlib
from typing import Dict, Any
from ..templates.rf_templates import RFTemplates

class ResourceAgent:
    def __init__(self):
        self.rf_templates = RFTemplates()
        self.projects_folder = "rf_projects"
        
    async def handle_create_resource(self, user_message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource creation requests"""
        resource_type = entities.get("resource_type", "keywords")
        resource_name = entities.get("resource_name", f"custom_{resource_type}")
        
        # Clean resource name
        resource_name = self._clean_resource_name(resource_name)
        
        if resource_type == "keywords":
            message = f"""I'll create a Robot Framework keywords resource file: **{resource_name}.robot**

This will include:
- Common UI interaction keywords
- Browser management keywords
- Assertion keywords
- Custom business logic keywords
- Proper documentation

Shall I create this keywords file?"""
        
        elif resource_type == "variables":
            message = f"""I'll create a Robot Framework variables resource file: **{resource_name}.robot**

This will include:
- Test data variables
- Configuration variables
- URL and environment variables
- UI element locators
- Test credentials (example structure)

Shall I create this variables file?"""
        
        else:
            message = f"""I'll create a Robot Framework resource file: **{resource_name}.robot**

This will include basic resource structure with keywords and variables.

Shall I create this resource file?"""
        
        return {
            "message": message,
            "requires_confirmation": True,
            "action": {
                "type": "create_resource",
                "resource_type": resource_type,
                "resource_name": resource_name
            }
        }
    
    async def create_resource_file(self, resource_type: str, resource_name: str) -> Dict[str, Any]:
        """Actually create the resource file"""
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
                (project_path / "resources").mkdir(exist_ok=True)
            
            resources_path = project_path / "resources"
            resource_file_path = resources_path / f"{resource_name}.robot"
            
            # Generate resource content based on type
            if resource_type == "keywords":
                content = self.rf_templates.get_custom_keywords_template(resource_name)
            elif resource_type == "variables":
                content = self.rf_templates.get_custom_variables_template(resource_name)
            else:
                content = self.rf_templates.get_generic_resource_template(resource_name, resource_type)
            
            # Write the resource file
            with open(resource_file_path, "w") as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"✅ Resource file '{resource_name}.robot' created successfully!\n\nFile: {resource_file_path.absolute()}\n\nYou can now import this resource in your test files with:\nResource    resources/{resource_name}.robot"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error creating resource file: {str(e)}"
            }
    
    async def create_custom_library(self, library_name: str, library_description: str = "") -> Dict[str, Any]:
        """Create a custom Python library for Robot Framework"""
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
                (project_path / "libraries").mkdir(exist_ok=True)
            
            libraries_path = project_path / "libraries"
            library_file_path = libraries_path / f"{library_name}.py"
            
            # Generate library content
            content = self.rf_templates.get_custom_library_template(library_name, library_description)
            
            # Write the library file
            with open(library_file_path, "w") as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"✅ Custom library '{library_name}.py' created successfully!\n\nFile: {library_file_path.absolute()}\n\nYou can now import this library in your test files with:\nLibrary    libraries/{library_name}.py"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error creating custom library: {str(e)}"
            }
    
    def _clean_resource_name(self, name: str) -> str:
        """Clean resource name to be filesystem safe"""
        # Replace spaces with underscores and remove special characters
        cleaned = "".join(c if c.isalnum() or c in "_-" else "_" for c in name.lower())
        # Remove multiple underscores
        while "__" in cleaned:
            cleaned = cleaned.replace("__", "_")
        return cleaned.strip("_") 