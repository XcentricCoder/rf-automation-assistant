# Robot Framework AI Assistant 🤖

A web-based automation testing assistant that helps you create and manage Robot Framework projects through natural language commands. Built with FastAPI, WebSockets, and Amazon Bedrock (Claude 3.5 Sonnet) integration.

![Robot Framework AI Assistant](https://img.shields.io/badge/Robot%20Framework-AI%20Assistant-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-WebSocket-red)
![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange)
![Claude](https://img.shields.io/badge/Claude-3.5%20Sonnet-purple)

## ✨ Features

### 🎯 Core Functionality
- **Natural Language Processing**: Chat with Claude AI to create Robot Framework projects
- **Project Structure Generation**: Complete RF project scaffolding with folders and files
- **Test Case Creation**: Generate test cases from descriptions
- **Resource Management**: Create keywords, variables, and custom libraries
- **Real-time Chat Interface**: Modern ChatGPT-like web interface
- **Confirmation Dialogs**: Safe file operations with user confirmation

### 🏗️ Architecture
- **Frontend**: Modern HTML/CSS/JS with WebSocket client
- **Backend**: Python FastAPI with async WebSocket support
- **AI Integration**: Amazon Bedrock with Claude 3.5 Sonnet for intent recognition
- **File Operations**: Automated Robot Framework file generation
- **Agent System**: Specialized agents for different RF components

### 🤖 AI Agents
- **Project Agent**: Creates complete RF project structures
- **Test Agent**: Generates test cases and test suites
- **Resource Agent**: Manages keywords, variables, and libraries

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- AWS Account with Bedrock access
- AWS CLI configured or AWS credentials
- Access to Claude 3.5 Sonnet in Amazon Bedrock
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd robot-framework-ai-assistant
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp env.example .env
# Edit .env and add your AWS credentials:
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key
# AWS_REGION=us-east-1
```

5. **Ensure Bedrock Access**
Make sure you have access to Claude 3.5 Sonnet in Amazon Bedrock in your AWS account.

6. **Run the application**
```bash
python run.py
```

7. **Open your browser**
Navigate to `http://localhost:8000`

## 📖 Usage Examples

### Creating a New Project
```
User: "Create an e-commerce automation project"
Assistant: "I'll create a Robot Framework project structure for 'e-commerce'..."
[Shows confirmation dialog with project structure]
User: Confirms
Assistant: "✅ Project created successfully!"
```

### Adding Test Cases
```
User: "Add a login test case"
Assistant: "I'll create a new Robot Framework test case..."
[Shows test case details for confirmation]
User: Confirms
Assistant: "✅ Test case 'Login Test' created successfully!"
```

### Creating Resources
```
User: "Create keywords resource file"
Assistant: "I'll create a Robot Framework keywords resource file..."
[Shows resource file structure]
User: Confirms
Assistant: "✅ Resource file created successfully!"
```

## 🗂️ Project Structure

```
robot-framework-ai-assistant/
├── app/
│   ├── agents/                 # AI agents for different RF components
│   │   ├── project_agent.py   # Project structure creation
│   │   ├── test_agent.py      # Test case generation
│   │   └── resource_agent.py  # Resource file management
│   ├── models/                # Pydantic models
│   │   └── chat_models.py     # Chat and response models
│   ├── services/              # External service integrations
│   │   └── openai_service.py  # Amazon Bedrock integration
│   ├── static/                # Frontend assets
│   │   ├── styles.css         # Modern CSS styles
│   │   └── script.js          # WebSocket client & UI
│   ├── templates/             # HTML templates & RF templates
│   │   ├── chat.html          # Main chat interface
│   │   └── rf_templates.py    # Robot Framework file templates
│   └── main.py                # FastAPI application
├── rf_projects/               # Generated RF projects (created automatically)
├── requirements.txt           # Python dependencies
├── env.example               # Environment variables template
└── README.md                 # This file
```

## 🎯 Generated Robot Framework Projects

When you create a project, the assistant generates a complete RF structure:

```
your_project/
├── tests/
│   ├── login_tests.robot       # Login functionality tests
│   └── main_flow_tests.robot   # Main application flow tests
├── resources/
│   ├── keywords.robot          # Reusable keywords
│   └── variables.robot         # Test variables and locators
├── libraries/
│   └── custom_library.py       # Custom Python library
└── requirements.txt            # RF dependencies
```

## 🛠️ Development

### Running in Development Mode
```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
python run.py

# Or directly with uvicorn
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Adding New Features

1. **New Agent**: Create in `app/agents/`
2. **New Templates**: Add to `app/templates/rf_templates.py`
3. **New Models**: Define in `app/models/`
4. **Frontend Updates**: Modify `app/static/` files

### Testing Generated Projects
```bash
# Navigate to generated project
cd rf_projects/your_project_name

# Install Robot Framework dependencies
pip install -r requirements.txt

# Run tests
robot tests/
```

## 🔧 Configuration

### Environment Variables
- `AWS_ACCESS_KEY_ID`: Your AWS access key (required)
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key (required)
- `AWS_REGION`: AWS region for Bedrock (default: us-east-1)
- `ENVIRONMENT`: Set to `development` for debug mode
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

### Amazon Bedrock Configuration
The assistant uses Claude 3.5 Sonnet via Amazon Bedrock. You can modify the model in `app/services/openai_service.py`:

```python
self.model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
```

### Setting up AWS Credentials

**Option 1: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

**Option 2: AWS CLI**
```bash
aws configure
```

**Option 3: .env file**
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
```

## 🎨 Features in Detail

### Chat Interface
- Modern, responsive design similar to ChatGPT
- Real-time WebSocket communication
- Auto-expanding text input
- Message formatting with markdown support
- Loading indicators and connection status

### AI Intent Recognition
- Natural language understanding for RF commands using Claude 3.5 Sonnet
- Context-aware entity extraction
- Fallback keyword matching when AI is unavailable
- Confidence scoring for intent classification

### File Generation
- Template-based RF file creation
- Customizable project structures
- Support for web and API testing projects
- Best practices built into templates

### Safety Features
- Confirmation dialogs before file operations
- Error handling and user feedback
- Connection status monitoring
- Graceful fallbacks

## 🔐 Security Notes

- AWS credentials are handled securely via environment variables
- No sensitive data is logged
- Bedrock API calls are made over HTTPS
- Local file operations are sandboxed to the project directory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Robot Framework community for the amazing testing framework
- Amazon for providing Bedrock and Claude AI capabilities
- Anthropic for developing Claude 3.5 Sonnet
- FastAPI for the excellent web framework
- The automation testing community for inspiration

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](issues) section
2. Review the documentation above
3. Create a new issue with detailed information

## 🔍 Troubleshooting

### Common Issues

**Bedrock Access Denied**
- Ensure you have proper IAM permissions for Bedrock
- Check that Claude 3.5 Sonnet is available in your region
- Verify your AWS credentials are correct

**Connection Issues**
- Check your internet connection
- Verify AWS region settings
- Ensure Bedrock service is available in your region

**Import Errors**
- Run `pip install -r requirements.txt`
- Check Python version (3.8+ required)
- Verify virtual environment is activated

---

**Happy Testing with Robot Framework! 🎯** 