import os
import pathlib
from typing import Dict, Any
from ..templates.rf_templates import RFTemplates
from ..services.llm_service import BedrockService
import json
import shutil
import json
class ProjectAgent:
    def __init__(self):
        self.rf_templates = RFTemplates()
        self.projects_folder = "rf_projects"
        self.llm_service = BedrockService()
        
    def build_project_structure_json(self, project_name, project_type):
        structure={
            "project_name" : project_name,
            "project_type" : project_type,
            "folder":[
                f"{project_name}/tests",
                f"{project_name}/resources",
                ],
            "files":[
                f"{project_name}/tests/login_tests.robot",
                f"{project_name}/tests/main_flow_tests.robot",
                f"{project_name}/resources/keywords.robot",
                f"{project_name}/resources/variables.robot",
                f"{project_name}/requirements.txt"
            ]
        }
        return structure
    
    def format_structure_tree(self, structure):
        import os

        project_name = structure.get("project_name", "project")
        folders = set(structure.get("folders", []))
        files = set(structure.get("files", []))

        # Build a nested dict representing the tree
        tree = {}

        def insert_path(tree, path):
            parts = path.replace("\\", "/").split("/")
            node = tree
            for part in parts:
                node = node.setdefault(part, {})

        def insert_file(tree, path):
            parts = path.replace("\\", "/").split("/")
            node = tree
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = None

        for folder in folders:
            insert_path(tree, folder)
        for file in files:
            insert_file(tree, file)

        def render(node, prefix=""):
            lines = []
            entries = sorted(node.items())
            for i, (name, child) in enumerate(entries):
                connector = "└── " if i == len(entries) - 1 else "├── "
                if child is None:
                    lines.append(f"{prefix}{connector}{name}")
                else:
                    lines.append(f"{prefix}{connector}{name}/")
                    extension = "    " if i == len(entries) - 1 else "│   "
                    lines.extend(render(child, prefix + extension))
            return lines

        tree_str = f"{project_name}/\n"
        if project_name in tree:
            tree_str += "\n".join(render(tree[project_name], ""))
        else:
            tree_str += "\n".join(render(tree, ""))
        return tree_str
    
    
    def project_exists_on_disk(self, project_name: str) -> bool:
        import os
        return os.path.isdir(os.path.join(self.projects_folder, project_name))

    def load_structure_from_disk(self, project_name: str) -> dict:
        import os
        project_path = os.path.join(self.projects_folder, project_name)
        structure = {
            "project_name": project_name,
            "project_type": None,
            "folders": [],
            "files": []
        }
        for root, dirs, files in os.walk(project_path):
            for d in dirs:
                structure["folders"].append(os.path.relpath(os.path.join(root, d), self.projects_folder))
            for f in files:
                structure["files"].append(os.path.relpath(os.path.join(root, f), self.projects_folder))
        return structure

    async def handle_create_project(self, classify_result: dict, user_message: str) -> Dict[str, Any]:
        """Handle project creation requests using classify_result from intent classifier"""
        entities = classify_result.get("entities", {})
        project_name = self._clean_project_name(entities.get("project_name", "automation_project"))
        project_type = entities.get("project_type", "web")
        # Use actual structure if project exists
        if self.project_exists_on_disk(project_name):
            structure = self.load_structure_from_disk(project_name)
        else:
            structure = self.build_project_structure_json(project_name, project_type)
        # Call manage_project_structure to process the user message and update the structure
        print(f"user_message: {user_message!r}")
        result = await self.manage_project_structure(user_message, structure)
        
        updated_structure = result.get("structure", structure)
        tree = self.format_structure_tree(updated_structure)
        return {
            "message": f"Updated Robot Framework project structure for '{project_name}':\n\n{tree}\nShall I proceed with creating this structure?",
            "structure": updated_structure,
            "requires_confirmation": True,
            "action": {
                "type": "create_project",
                "project_name": project_name,
                "project_type": project_type
            }
        }
    
    async def create_project_structure(self, project_name: str, project_type: str = "web") -> Dict[str, Any]:
        """Actually create the project files"""
        try:
            print(f"[DEBUG] Starting project structure creation for: {project_name} (type: {project_type})")
            # Create main project directory
            project_path = pathlib.Path(self.projects_folder) / project_name
            print(f"[DEBUG] Creating main project directory at: {project_path}")
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            print(f"[DEBUG] Creating subdirectories: tests, resources")
            (project_path / "tests").mkdir(exist_ok=True)
            (project_path / "resources").mkdir(exist_ok=True)
            #(project_path / "libraries").mkdir(exist_ok=True)
            
            # Create test files
            print(f"[DEBUG] Creating test files...")
            await self._create_test_files(project_path, project_type)
            
            # Create resource files
            print(f"[DEBUG] Creating resource files...")
            await self._create_resource_files(project_path, project_type)
            
            # Create requirements.txt
            print(f"[DEBUG] Creating requirements.txt...")
            await self._create_requirements_file(project_path)
            
            # Create custom library
            #print(f"[DEBUG] Creating custom library...")
            #await self._create_custom_library(project_path, project_name)
            
            print(f"[DEBUG] Project structure creation complete for: {project_name}")
            return {
                "success": True,
                "message": f"✅ Project '{project_name}' created successfully!\n\nFiles created in: {project_path.absolute()}\n\nYou can now open this folder in VS Code to see your Robot Framework project."
            }
            
        except Exception as e:
            print(f"[DEBUG] Exception occurred during project creation: {e}")
            return {
                "success": False,
                "message": f"❌ Error creating project: {str(e)}"
            }
    
    async def _create_test_files(self, project_path: pathlib.Path, project_type: str):
        """Create test robot files"""
        tests_path = project_path / "tests"
        
        # Login tests
        login_test = self.rf_templates.get_login_test_template(project_type)
        with open(tests_path / "login_tests.robot", "w") as f:
            f.write(login_test)
        
        # Main flow tests
        main_test = self.rf_templates.get_main_flow_test_template(project_type)
        with open(tests_path / "main_flow_tests.robot", "w") as f:
            f.write(main_test)
    
    async def _create_resource_files(self, project_path: pathlib.Path, project_type: str):
        """Create resource files"""
        resources_path = project_path / "resources"
        
        # Keywords file
        keywords = self.rf_templates.get_keywords_template(project_type)
        with open(resources_path / "keywords.robot", "w") as f:
            f.write(keywords)
        
        # Variables file
        variables = self.rf_templates.get_variables_template(project_type)
        with open(resources_path / "variables.robot", "w") as f:
            f.write(variables)
    
    async def _create_requirements_file(self, project_path: pathlib.Path):
        """Create requirements.txt"""
        requirements = self.rf_templates.get_requirements_template()
        with open(project_path / "requirements.txt", "w") as f:
            f.write(requirements)
    
    #async def _create_custom_library(self, project_path: pathlib.Path, project_name: str):
    #    """Create custom Python library"""
    #    try:
    #        print(f"[DEBUG] Entering _create_custom_library for project: {project_name}")
    #        libraries_path = project_path / "libraries"
    #        print(f"[DEBUG] Library path: {libraries_path}")
    #        library_code = self.rf_templates.get_custom_library_template(project_name)
    #        print(f"[DEBUG] Library code generated (first 100 chars): {library_code[:100]}")
    #        with open(libraries_path / "custom_library.py", "w") as f:
    #            f.write(library_code)
    #        print(f"[DEBUG] custom_library.py written successfully.")
    #    except Exception as e:
    #        print(f"[DEBUG] Exception in _create_custom_library: {e}")
    #        raise
    
    async def manage_project_structure(self, user_message: str, structure_json: dict) -> dict:
        """
        Manage the project structure based on user and system instructions.
        """
        import os
        import json

        prompt_file = 'manage_structure_prompt.txt'
        if os.path.exists(prompt_file):
            with open(prompt_file, 'r', encoding='utf-8') as f:
                system_prompt_text = f.read()
            print(f"[DEBUG] Read system prompt from {prompt_file}")
        else:
            system_prompt_text = (
                "You are a project structure management assistant. "
                "Given a user instruction and the current project structure in JSON, "
                "decide what action to take (add_file, delete_file, add_folder, delete_folder), "
                "the target (file/folder name), and content (if adding a file). Respond in JSON."
            )
            print(f"[DEBUG] {prompt_file} not found. Using default system prompt.")

        prompt = f"""{system_prompt_text}\n\nCurrent project structure (JSON):\n{json.dumps(structure_json, indent=2)}\n\nUser instruction:\n{user_message}\n\nRespond ONLY 
        with the JSON list of actions."""
        print(f"[DEBUG] LLM prompt for manage_project_structure:\n{prompt}")
        # Change LLM call from classify_intent to invoke_claude
        llm_result = self.llm_service.invoke_claude(prompt)
        print(f"[DEBUG] LLM result: {llm_result}")

        # Extract the text content if present
        if isinstance(llm_result, dict) and "content" in llm_result and isinstance(llm_result["content"], list):
            llm_text = llm_result["content"][0].get("text", "")
        else:
            llm_text = llm_result

        actions = json.loads(llm_text)

        # If it's a dict with action_type, wrap in a list
        if isinstance(actions, dict) and "action_type" in actions and "target" in actions:
            actions = [actions]

        # If it's a list of dicts, proceed
        if isinstance(actions, list) and all(isinstance(a, dict) and "action_type" in a and "target" in a for a in actions):
            pass  # Good to go
        else:
            # Fallback: try to infer from intent/entities dict
            print("[DEBUG] LLM output not in expected format, attempting fallback...")
            fallback_actions = []
            if isinstance(llm_result, dict) and "entities" in llm_result:
                entities = llm_result["entities"]
                # Only do folder/file fallback if intent is NOT create_project
                # Only skip fallback if project does NOT exist (i.e., this is a true new project creation)
                skip_fallback = (
                    llm_result.get("intent") == "create_project"
                    and not self.project_exists_on_disk(structure_json.get("project_name", "automation_project"))
                )
                if not skip_fallback:
                    # Fallback for add_folder
                    folder_name = entities.get("folder_name")
                    folder_list = []
                    if folder_name:
                        if isinstance(folder_name, list):
                            folder_list = folder_name
                        elif isinstance(folder_name, str):
                            folder_list = [f.strip() for f in folder_name.split(",") if f.strip()]
                    for folder in folder_list:
                        fallback_actions.append({
                            "action_type": "add_folder",
                            "target": f"{structure_json.get('project_name', 'automation_project')}/{folder}" if not folder.startswith(structure_json.get('project_name',
                         'automation_project')) else folder
                        })
                    # Fallback for add_file
                    file_name = entities.get("file_name")
                    file_list = []
                    if file_name:
                        if isinstance(file_name, list):
                            file_list = file_name
                        elif isinstance(file_name, str):
                            file_list = [f.strip() for f in file_name.split(",") if f.strip()]
                    for file in file_list:
                        fallback_actions.append({
                            "action_type": "add_file",
                            "target": file,
                            "content": ""
                        })
            if fallback_actions:
                actions = fallback_actions
            else:
                return {"success": False, "message": "LLM output could not be parsed as actions.", "structure": structure_json}

        summary = []
        updated_structure = structure_json.copy()
        for action in actions:
            action_type = action.get("action_type")
            target = action.get("target")
            content = action.get("content", "")
            if action_type == "create_project":
                # Call project creation logic
                project_name = action.get("project_name") or updated_structure.get("project_name", "automation_project")
                project_type = action.get("project_type") or updated_structure.get("project_type", "web")
                result = await self.create_project_structure(project_name, project_type)
                updated_structure = result.get("structure", updated_structure)
                summary.append(f"Created project: {project_name}")
            elif action_type == "add_folder" and target:
                self.create_folder(target)
                updated_structure.setdefault("folders", []).append(target)
                summary.append(f"Added folder: {target}")
            elif action_type == "add_file" and target:
                self.create_file(target, content)
                updated_structure.setdefault("files", []).append(target)
                summary.append(f"Added file: {target}")
            elif action_type == "delete_folder" and target:
                self.delete_folder(target)
                if "folders" in updated_structure and target in updated_structure["folders"]:
                    updated_structure["folders"].remove(target)
                summary.append(f"Deleted folder: {target}")
            elif action_type == "delete_file" and target:
                self.delete_file(target)
                if "files" in updated_structure and target in updated_structure["files"]:
                    updated_structure["files"].remove(target)
                summary.append(f"Deleted file: {target}")
            else:
                summary.append(f"Unknown or incomplete action: {action}")

        return {
            "success": True,
            "message": "; ".join(summary),
            "structure": updated_structure
        }
    
    def _clean_project_name(self, name: str) -> str:
        """Clean project name to be filesystem safe"""
        # Handle None or empty values
        if not name:
            return "automation_project"
        
        # Ensure name is a string
        name = str(name)
        
        # Replace spaces with underscores and remove special characters
        cleaned = "".join(c if c.isalnum() or c in "_-" else "_" for c in name.lower())
        # Remove multiple underscores
        while "__" in cleaned:
            cleaned = cleaned.replace("__", "_")
        return cleaned.strip("_") 

    def create_folder(self, folder_path: str) -> bool:
        """Create a folder in the project directory.""" 
        try:
            full_path = pathlib.Path(self.projects_folder) / folder_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"[DEBUG] Created folder: {full_path}")
            return True
        except Exception as e:
            print(f"[DEBUG] Error creating folder {folder_path}: {e}")
            return False

    def create_file(self, file_path: str, content: str = "") -> bool:
        """Create a file in the project directory with optional content."""
        try:
            full_path = pathlib.Path(self.projects_folder) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[DEBUG] Created file: {full_path}")
            return True
        except Exception as e:
            print(f"[DEBUG] Error creating file {file_path}: {e}")
            return False

    def delete_folder(self, folder_path: str) -> bool:
        """Delete a folder and all its contents in the project directory."""
        try:
            full_path = pathlib.Path(self.projects_folder) / folder_path
            shutil.rmtree(full_path)
            print(f"[DEBUG] Deleted folder: {full_path}")
            return True
        except Exception as e:
            print(f"[DEBUG] Error deleting folder {folder_path}: {e}")
            return False

    def delete_file(self, file_path: str) -> bool:
        """Delete a file in the project directory."""
        try:
            full_path = pathlib.Path(self.projects_folder) / file_path
            full_path.unlink()
            print(f"[DEBUG] Deleted file: {full_path}")
            return True
        except Exception as e:
            print(f"[DEBUG] Error deleting file {file_path}: {e}")
            return False
        
        