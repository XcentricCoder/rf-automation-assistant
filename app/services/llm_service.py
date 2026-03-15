import boto3
import json
import os
from typing import Dict, Any

class BedrockService:
    def __init__(self):
        # Initialize AWS Bedrock client
        self.bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        self.model_id = ""
    
    def invoke_claude(self, prompt_text: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Invoke Claude model via Bedrock"""
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "top_k": 250,
                "stop_sequences": [],
                "temperature": 0.1,  # Low temperature for more consistent responses
                "top_p": 0.999,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt_text
                            }
                        ]
                    }
                ]
            }

            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body)
            )

            response_body = json.loads(response['body'].read())
            return response_body
            
        except Exception as e:
            print(f"Bedrock API error: {e}")
            raise e
    
    async def classify_intent(self, user_message: str) -> Dict[str, Any]:
        """Classify user intent and extract entities using Claude"""
        # Validate input
        if not user_message or not isinstance(user_message, str):
            return self._fallback_intent_classification("")
        user_message = user_message.strip()
        if not user_message:
            return self._fallback_intent_classification("")
        try:
            # Try to read prompt template from file
            prompt_file = 'intent_prompt.txt'
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_template = f.read()
                    print(f"DEBUG: Prompt template: {prompt_template}")
                prompt = prompt_template.format(user_message=user_message)
            else:
                print(f"DEBUG: Prompt template not found: {prompt_file}")
            prompt = f"""You are an expert in Robot Framework automation. Analyze this user request and classify the intent:

User message: \"{user_message}\"

Classify into one of these intents:
- create_project: User wants to create a new RF project structure
- create_test: User wants to create test cases
- create_resource: User wants to create resource files (keywords, variables)
- confirm: User is confirming an action (yes, confirm, proceed, etc.)
- deny: User is denying an action (no, cancel, stop, etc.)
- unknown: Cannot determine intent

Also extract these entities if present:
- project_name: Name of the project
- project_type: Type of project (web, api, mobile, desktop)
- test_name: Name of test case
- test_description: Description of what test should do
- resource_type: Type of resource (keywords, variables, library)

Return ONLY a valid JSON response in this exact format:
{{
    "intent": "intent_name",
    "entities": {{
        "project_name": "extracted_name_or_null",
        "project_type": "web_or_api_or_mobile_or_desktop",
        "test_name": "test_name_or_null",
        "test_description": "description_or_null",
        "resource_type": "keywords_or_variables_or_library"
    }},
    "confidence": 0.95
}}

Do not include any other text, only the JSON response."""
            response = self.invoke_claude(prompt, max_tokens=500)
            
            # Extract the text content from Claude's response
            content = response.get('content', [])
            if content and len(content) > 0:
                result_text = content[0].get('text', '').strip()
                print(f"result_text: {result_text!r}")
                # Try to parse JSON response
                try:
                    result = json.loads(result_text)
                    print(f"result: {result!r}")
                    return result
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    print(f"[DEBUG] JSON parsing failed ")
                    return self._fallback_intent_classification(user_message)
            else:
                return self._fallback_intent_classification(user_message)
                
        except Exception as e:
            print(f"Bedrock API error: {e}")
            return self._fallback_intent_classification(user_message)
    
    def _fallback_intent_classification(self, user_message: str) -> Dict[str, Any]:
        """Fallback intent classification using keyword matching"""
        # Validate input and provide safe defaults
        print(f"DEBUG: Fallback intent classification: {user_message}")
        if not user_message or not isinstance(user_message, str):
            return {"intent": "unknown", "entities": {}, "confidence": 0.1}
        
        user_message = user_message.strip()
        if not user_message:
            return {"intent": "unknown", "entities": {}, "confidence": 0.1}
        
        message_lower = user_message.lower()
        
        # Simple keyword-based classification
        if any(word in message_lower for word in ["create project", "new project", "project structure", "e-commerce", "automation project"]):
            # Extract project name from common patterns
            project_name = "automation_project"
            if "e-commerce" in message_lower or "ecommerce" in message_lower:
                project_name = "ecommerce_automation"
            elif "web" in message_lower:
                project_name = "web_automation"
            elif "api" in message_lower:
                project_name = "api_automation"
            
            return {
                "intent": "create_project",
                "entities": {
                    "project_name": project_name, 
                    "project_type": "api" if "api" in message_lower else "web"
                },
                "confidence": 0.7,
                "message": f"DEBUG: Fallback intent classification: {user_message}"
            }
        elif any(word in message_lower for word in ["create test", "add test", "test case", "login test", "registration test"]):
            test_name = "sample_test"
            test_description = "Basic test case"
            
            if "login" in message_lower:
                test_name = "Login Test"
                test_description = "Test user login functionality"
            elif "registration" in message_lower or "register" in message_lower:
                test_name = "User Registration Test"
                test_description = "Test user registration functionality"
            elif "checkout" in message_lower:
                test_name = "Checkout Test"
                test_description = "Test checkout process"
            
            return {
                "intent": "create_test", 
                "entities": {
                    "test_name": test_name, 
                    "test_description": test_description,
                    "test_suite": "custom_tests"
                },
                "confidence": 0.7,
                "message": f"DEBUG: Fallback intent classification: {user_message}"
            }
        elif any(word in message_lower for word in ["resource", "keyword", "variable", "library"]):
            resource_type = "keywords"
            if "variable" in message_lower:
                resource_type = "variables"
            elif "library" in message_lower:
                resource_type = "library"
            
            return {
                "intent": "create_resource",
                "entities": {"resource_type": resource_type},
                "confidence": 0.7
            }
        elif any(word in message_lower for word in ["yes", "confirm", "proceed", "ok", "sure"]):
            return {"intent": "confirm", "entities": {}, "confidence": 0.9}
        elif any(word in message_lower for word in ["no", "cancel", "stop", "deny", "abort"]):
            return {"intent": "deny", "entities": {}, "confidence": 0.9}
        else:
            return {"intent": "unknown", "entities": {}, "confidence": 0.5}

# Alias for backward compatibility
OpenAIService = BedrockService 
