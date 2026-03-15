from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import json
import asyncio 
import traceback
from typing import List
import os 
from dotenv import load_dotenv
from .agents.project_agent import ProjectAgent
from .agents.test_agent import TestAgent
from .agents.resource_agent import ResourceAgent
from .services.llm_service import BedrockService
from .models.chat_models import ChatMessage, ChatResponse

# Load environment variables
load_dotenv()

app = FastAPI(title="Robot Framework AI Assistant")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Initialize services and agents
bedrock_service = BedrockService()
project_agent = ProjectAgent()
test_agent = TestAgent()
resource_agent = ResourceAgent()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.pending_actions: dict = {}  # Store pending actions per connection

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        # Clean up pending actions
        connection_id = id(websocket)
        if connection_id in self.pending_actions:
            del self.pending_actions[connection_id]

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    def store_pending_action(self, websocket: WebSocket, action: dict):
        connection_id = id(websocket)
        self.pending_actions[connection_id] = action

    def get_pending_action(self, websocket: WebSocket):
        connection_id = id(websocket)
        return self.pending_actions.get(connection_id)

    def clear_pending_action(self, websocket: WebSocket):
        connection_id = id(websocket)
        if connection_id in self.pending_actions:
            del self.pending_actions[connection_id]

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            action_data = message_data.get("action")
            
            # Process the message with AI
            response = await process_user_message(user_message, websocket, action_data)
            
            # Send response back to client using model_dump instead of dict
            await manager.send_message(json.dumps(response.model_dump()), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def process_user_message(user_message: str, websocket: WebSocket, action_data=None) -> ChatResponse:
    """Process user message and route to appropriate agent"""
    try:
        # Validate user message
        if not user_message or not isinstance(user_message, str):
            return ChatResponse(
                message="Please enter a message to get started. You can ask me to create Robot Framework projects, test cases, or resources.",
                type="assistant"
            )
        
        user_message = user_message.strip()
        if not user_message:
            return ChatResponse(
                message="Please enter a message to get started. You can ask me to create Robot Framework projects, test cases, or resources.",
                type="assistant"
            )
        
        # Check if this is a confirmation message
        if user_message.lower() in ['yes', 'confirm', 'proceed', 'ok']:
            pending_action = manager.get_pending_action(websocket)
            if pending_action:
                manager.clear_pending_action(websocket)
                return await execute_confirmed_action(pending_action)
            else:
                return ChatResponse(
                    message="There's no pending action to confirm.",
                    type="assistant"
                )
        
        if user_message.lower() in ['no', 'cancel', 'stop', 'deny']:
            manager.clear_pending_action(websocket)
            return ChatResponse(
                message="Action cancelled. How else can I help you?",
                type="assistant"
            )
        
        # Get intent from Bedrock/Claude
        intent_result = await bedrock_service.classify_intent(user_message)
        ALLOWED_INTENTS = {"create_project", "create_test", "create_resource", "confirm", "deny", "unknown"}
        intent = intent_result.get("intent", "unknown")
        if intent not in ALLOWED_INTENTS:
            print(f"ERROR: Invalid intent from LLM: {intent}")
        # Optionally: retry, fallback, or show a specific error message
            return ChatResponse(
        message=f"Sorry, I didn't understand your request (invalid intent: {intent}). Please rephrase.",
        type="error"
    )
        entities = intent_result.get("entities", {})
        
        # Debug logging
        print(f"DEBUG: User message: {user_message}")
        print(f"DEBUG: Intent result: {intent_result}")
        print(f"DEBUG: Intent: {intent}")
        print(f"DEBUG: Entities: {entities}")
        
        response_text = ""
        requires_confirmation = False
        suggested_action = None
        
        # Route to appropriate agent based on intent
        if intent == "create_project":
            result = await project_agent.handle_create_project(intent_result, user_message)
            response_text = result["message"]
            requires_confirmation = result.get("requires_confirmation", False)
            suggested_action = result.get("action")
            
            if requires_confirmation and suggested_action:
                manager.store_pending_action(websocket, suggested_action)
            
        elif intent == "create_test":
            result = await test_agent.handle_create_test(user_message, entities)
            response_text = result["message"]
            requires_confirmation = result.get("requires_confirmation", False)
            suggested_action = result.get("action")
            
            if requires_confirmation and suggested_action:
                manager.store_pending_action(websocket, suggested_action)
            
        elif intent == "create_resource":
            result = await resource_agent.handle_create_resource(user_message, entities)
            response_text = result["message"]
            requires_confirmation = result.get("requires_confirmation", False)
            suggested_action = result.get("action")
            
            if requires_confirmation and suggested_action:
                manager.store_pending_action(websocket, suggested_action)
            
        else:
            response_text = """I understand you want to work with Robot Framework. Could you be more specific? Here are some examples:

**Project Creation:**
- "Create an e-commerce automation project"
- "Set up a web testing project"
- "Create an API testing project"

**Test Cases:**
- "Add a login test case"
- "Create a user registration test"
- "Add API endpoint tests"

**Resources:**
- "Create keywords resource file"
- "Add variables for web elements"
- "Create custom library for utilities"

What would you like to create?"""
        
        return ChatResponse(
            message=response_text,
            type="assistant",
            requires_confirmation=requires_confirmation,
            suggested_action=suggested_action
        )
        
    except Exception as e:
        print(f"ERROR in process_user_message: {str(e)}")
        traceback.print_exc()
        return ChatResponse(
            message=f"Sorry, I encountered an error: {str(e)}. Please try again or rephrase your request.",
            type="error"
        )

async def execute_confirmed_action(action: dict) -> ChatResponse:
    """Execute the confirmed action"""
    try:
        action_type = action.get("type")
        
        if action_type == "create_project":
            result = await project_agent.create_project_structure(
                action["project_name"],
                action["project_type"]
            )
            
        elif action_type == "create_test":
            result = await test_agent.create_test_case(
                action["test_name"],
                action["test_description"],
                action["test_suite"]
            )
            
        elif action_type == "create_resource":
            result = await resource_agent.create_resource_file(
                action["resource_type"],
                action["resource_name"]
            )
            
        else:
            return ChatResponse(
                message="Unknown action type. Please try again.",
                type="error"
            )
        
        if result.get("success"):
            return ChatResponse(
                message=result["message"],
                type="assistant"
            )
        else:
            return ChatResponse(
                message=result["message"],
                type="error"
            )
            
    except Exception as e:
        return ChatResponse(
            message=f"Error executing action: {str(e)}",
            type="error"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 