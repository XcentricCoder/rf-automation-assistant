class RFTemplates:
    """Templates for Robot Framework files"""
    
    def get_login_test_template(self, project_type: str = "web") -> str:
        """Generate login test template based on project type"""
        if project_type == "web":
            return """*** Settings ***
Documentation    Login functionality tests
Resource         ../resources/keywords.robot
Resource         ../resources/variables.robot
Library          SeleniumLibrary
Suite Setup      Open Browser To Login Page
Suite Teardown   Close Browser

*** Test Cases ***
Valid Login Test
    [Documentation]    Test successful login with valid credentials
    [Tags]             login    positive    smoke
    Input Username     ${VALID_USERNAME}
    Input Password     ${VALID_PASSWORD}
    Submit Credentials
    Login Should Succeed
    
Invalid Username Test
    [Documentation]    Test login with invalid username
    [Tags]             login    negative
    Input Username     invalid_user
    Input Password     ${VALID_PASSWORD}
    Submit Credentials
    Login Should Fail With Message    Invalid credentials
    
Invalid Password Test
    [Documentation]    Test login with invalid password
    [Tags]             login    negative
    Input Username     ${VALID_USERNAME}
    Input Password     invalid_password
    Submit Credentials
    Login Should Fail With Message    Invalid credentials
    
Empty Credentials Test
    [Documentation]    Test login with empty credentials
    [Tags]             login    negative
    Input Username     ${EMPTY}
    Input Password     ${EMPTY}
    Submit Credentials
    Login Should Fail With Message    Please enter username and password
"""
        else:
            return """*** Settings ***
Documentation    API Login functionality tests
Resource         ../resources/keywords.robot
Resource         ../resources/variables.robot
Library          RequestsLibrary

*** Test Cases ***
Valid API Login Test
    [Documentation]    Test successful API login with valid credentials
    [Tags]             api    login    positive
    Create Session    api    ${BASE_URL}
    ${response}=      POST Request    api    /auth/login    data=${LOGIN_DATA}
    Should Be Equal As Strings    ${response.status_code}    200
    Should Contain    ${response.json()['message']}    Login successful
"""
    
    def get_main_flow_test_template(self, project_type: str = "web") -> str:
        """Generate main flow test template"""
        if project_type == "web":
            return """*** Settings ***
Documentation    Main application flow tests
Resource         ../resources/keywords.robot
Resource         ../resources/variables.robot
Library          SeleniumLibrary
Suite Setup      Open Browser And Login
Suite Teardown   Close Browser

*** Test Cases ***
Complete User Journey Test
    [Documentation]    Test complete user workflow from login to logout
    [Tags]             e2e    smoke
    Navigate To Dashboard
    Verify Dashboard Elements
    Navigate To Profile
    Update Profile Information
    Save Changes
    Verify Success Message
    Logout User
    
Search Functionality Test
    [Documentation]    Test search functionality
    [Tags]             search    functional
    Navigate To Search Page
    Enter Search Term    automation testing
    Click Search Button
    Verify Search Results
    
Navigation Test
    [Documentation]    Test main navigation functionality
    [Tags]             navigation    functional
    Verify Main Menu
    Click Menu Item    Products
    Verify Page Title    Products
    Click Menu Item    Services
    Verify Page Title    Services
    Click Menu Item    Contact
    Verify Page Title    Contact
"""
        else:
            return """*** Settings ***
Documentation    API Main flow tests
Resource         ../resources/keywords.robot
Resource         ../resources/variables.robot
Library          RequestsLibrary

*** Test Cases ***
Complete API Workflow Test
    [Documentation]    Test complete API workflow
    [Tags]             api    e2e
    Authenticate API
    Create New Resource
    Retrieve Resource
    Update Resource
    Delete Resource
    Verify Resource Deleted
"""
    
    def get_keywords_template(self, project_type: str = "web") -> str:
        """Generate keywords template"""
        if project_type == "web":
            return """*** Settings ***
Documentation    Common keywords for web automation
Library          SeleniumLibrary

*** Keywords ***
Open Browser To Login Page
    [Documentation]    Open browser and navigate to login page
    Open Browser    ${LOGIN_URL}    ${BROWSER}
    Maximize Browser Window
    Wait Until Page Contains Element    ${USERNAME_FIELD}
    
Input Username
    [Documentation]    Enter username in the username field
    [Arguments]    ${}
    Input Text    ${USERNAME_FIELD}    ${username}
    
Input Password
    [Documentation]    Enter password in the password fielusernamed
    [Arguments]    ${password}
    Input Password    ${PASSWORD_FIELD}    ${password}
    
Submit Credentials
    [Documentation]    Click the login button
    Click Button    ${LOGIN_BUTTON}
    
Login Should Succeed
    [Documentation]    Verify successful login
    Wait Until Page Contains Element    ${DASHBOARD_ELEMENT}
    Page Should Contain    Welcome
    
Login Should Fail With Message
    [Documentation]    Verify login failure with specific error message
    [Arguments]    ${error_message}
    Wait Until Page Contains    ${error_message}
    Page Should Contain    ${error_message}
    
Open Browser And Login
    [Documentation]    Open browser and perform login
    Open Browser To Login Page
    Input Username    ${VALID_USERNAME}
    Input Password    ${VALID_PASSWORD}
    Submit Credentials
    Login Should Succeed
    
Navigate To Dashboard
    [Documentation]    Navigate to dashboard page
    Click Link    ${DASHBOARD_LINK}
    Wait Until Page Contains Element    ${DASHBOARD_ELEMENT}
    
Verify Dashboard Elements
    [Documentation]    Verify key dashboard elements are present
    Page Should Contain Element    ${DASHBOARD_HEADER}
    Page Should Contain Element    ${DASHBOARD_MENU}
    Page Should Contain Element    ${USER_INFO}
"""
        else:
            return """*** Settings ***
Documentation    Common keywords for API automation
Library          RequestsLibrary
Library          Collections

*** Keywords ***
Authenticate API
    [Documentation]    Authenticate with the API
    Create Session    api    ${BASE_URL}
    ${auth_data}=    Create Dictionary    username=${API_USERNAME}    password=${API_PASSWORD}
    ${response}=     POST Request    api    /auth/login    data=${auth_data}
    Should Be Equal As Strings    ${response.status_code}    200
    ${token}=        Get From Dictionary    ${response.json()}    token
    Set Suite Variable    ${AUTH_TOKEN}    ${token}
    
Create New Resource
    [Documentation]    Create a new resource via API
    ${headers}=      Create Dictionary    Authorization=Bearer ${AUTH_TOKEN}
    ${data}=         Create Dictionary    name=Test Resource    type=automation
    ${response}=     POST Request    api    /resources    data=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    201
    ${resource_id}=  Get From Dictionary    ${response.json()}    id
    Set Suite Variable    ${RESOURCE_ID}    ${resource_id}
"""
    
    def get_variables_template(self, project_type: str = "web") -> str:
        """Generate variables template"""
        if project_type == "web":
            return """*** Variables ***
# Browser Configuration
${BROWSER}              Chrome
${IMPLICIT_WAIT}        10s
${EXPLICIT_WAIT}        30s

# Application URLs
${BASE_URL}             https://example.com
${LOGIN_URL}            ${BASE_URL}/login
${DASHBOARD_URL}        ${BASE_URL}/dashboard

# Test Credentials
${VALID_USERNAME}       testuser@example.com
${VALID_PASSWORD}       TestPassword123!
${INVALID_USERNAME}     invalid@example.com
${INVALID_PASSWORD}     wrongpassword

# UI Elements - Login Page
${USERNAME_FIELD}       id=username
${PASSWORD_FIELD}       id=password
${LOGIN_BUTTON}         id=login-btn
${ERROR_MESSAGE}        css=.error-message

# UI Elements - Dashboard
${DASHBOARD_ELEMENT}    css=.dashboard
${DASHBOARD_HEADER}     css=.dashboard-header
${DASHBOARD_MENU}       css=.main-menu
${DASHBOARD_LINK}       css=a[href='/dashboard']
${USER_INFO}            css=.user-info

# Search Elements
${SEARCH_FIELD}         id=search-input
${SEARCH_BUTTON}        id=search-btn
${SEARCH_RESULTS}       css=.search-results

# Navigation Elements
${MAIN_MENU}            css=.main-navigation
${PRODUCTS_LINK}        css=a[href='/products']
${SERVICES_LINK}        css=a[href='/services']
${CONTACT_LINK}         css=a[href='/contact']

# Test Data
${SEARCH_TERM}          automation testing
${PROFILE_NAME}         John Doe
${PROFILE_EMAIL}        john.doe@example.com
"""
        else:
            return """*** Variables ***
# API Configuration
${BASE_URL}             https://api.example.com/v1
${API_TIMEOUT}          30s

# API Credentials
${API_USERNAME}         api_user
${API_PASSWORD}         api_password123
${API_KEY}              your_api_key_here

# API Endpoints
${LOGIN_ENDPOINT}       /auth/login
${USERS_ENDPOINT}       /users
${RESOURCES_ENDPOINT}   /resources
${HEALTH_ENDPOINT}      /health

# Test Data
${TEST_USER_DATA}       {"name": "Test User", "email": "test@example.com"}
${TEST_RESOURCE_DATA}   {"name": "Test Resource", "type": "automation"}

# Expected Responses
${SUCCESS_STATUS}       200
${CREATED_STATUS}       201
${NOT_FOUND_STATUS}     404
${UNAUTHORIZED_STATUS}  401
"""
    
    def get_requirements_template(self) -> str:
        """Generate requirements.txt for Robot Framework project"""
        return """# Robot Framework and core libraries
robotframework==6.1.1
robotframework-seleniumlibrary==6.1.0
robotframework-requests==0.9.5
robotframework-databaselibrary==1.2.4

# Web drivers
webdriver-manager==4.0.1

# Additional libraries
selenium==4.15.2
requests==2.31.0
openpyxl==3.1.2
PyYAML==6.0.1

# Development and reporting
robotframework-lint==1.1
robotframework-pabot==2.16.0
"""
    
    def get_custom_library_template(self, library_name: str, description: str = "") -> str:
        """Generate custom Python library template"""
        print(f"[DEBUG] Entering get_custom_library_template with library_name: {library_name}, description: {description}")
        class_name = "".join(word.capitalize() for word in library_name.split("_"))
        
        return f"""\"\"\"
{library_name.replace('_', ' ').title()} - Custom Robot Framework Library
{description if description else 'Custom library for automation testing'}
\"\"\"

from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
import time
import random
import string


class {class_name}:
    \"\"\"Custom Robot Framework Library for {library_name.replace('_', ' ').title()}\"\"\"
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'
    
    def __init__(self):
        self.builtin = BuiltIn()
    
    @keyword
    def generate_random_string(self, length=10):
        \"\"\"Generate a random string of specified length
        
        Args:
            length (int): Length of the string to generate
            
        Returns:
            str: Random string
        \"\"\"
        return ''.join(random.choices(string.ascii_letters + string.digits, k=int(length)))
    
    @keyword
    def wait_for_element_and_click(self, locator, timeout=30):
        \"\"\"Wait for element to be visible and click it
        
        Args:
            locator (str): Element locator
            timeout (int): Maximum wait time in seconds
        \"\"\"
        selenium_lib = self.builtin.get_library_instance('SeleniumLibrary')
        selenium_lib.wait_until_element_is_visible(locator, timeout)
        selenium_lib.click_element(locator)
    
    @keyword
    def generate_test_email(self, domain='example.com'):
        \"\"\"Generate a test email address
        
        Args:
            domain (str): Email domain
            
        Returns:
            str: Test email address
        \"\"\"
        user = self.generate_random_string(8).lower()
        return f"test_{username}@{domain}"
    
    @keyword
    def log_test_info(self, message):
        \"\"\"Log test information with timestamp
        
        Args:
            message (str): Message to log
        \"\"\"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.builtin.log(f"[{timestamp}] {message}", console=True)
    
    @keyword
    def verify_element_count(self, locator, expected_count):
        \"\"\"Verify the number of elements matching the locator
        
        Args:
            locator (str): Element locator
            expected_count (int): Expected number of elements
        \"\"\"
        selenium_lib = self.builtin.get_library_instance('SeleniumLibrary')
        elements = selenium_lib.get_webelements(locator)
        actual_count = len(elements)
        
        if actual_count != int(expected_count):
            raise AssertionError(
                f"Expected {expected_count} elements, but found {actual_count}"
            )
        
        self.builtin.log(f"Verified {actual_count} elements found for locator: {locator}")
"""
    
    def get_test_case_template(self, test_name: str, test_description: str, test_suite: str) -> str:
        """Generate a complete test case file"""
        return f"""*** Settings ***
Documentation    {test_suite.replace('_', ' ').title()} Test Suite
...              {test_description}
Resource         ../resources/keywords.robot
Resource         ../resources/variables.robot
Library          PlaywrightLibrary

*** Test Cases ***
{test_name}
    [Documentation]    {test_description}
    [Tags]             {test_suite.lower()}    functional
    [Setup]            Open Browser To Login Page
    [Teardown]         Close Browser
    
    # Test Steps
    Log Test Info      Starting test: {test_name}
    Input Username     ${{VALID_USERNAME}}
    Input Password     ${{VALID_PASSWORD}}
    Submit Credentials
    Login Should Succeed
    
    # Add your test steps here
    Log Test Info      Test completed successfully
    
    # Verification
    Page Should Contain    Welcome
"""
    
    def get_single_test_case(self, test_name: str, test_description: str) -> str:
        """Generate a single test case to add to existing suite"""
        return f"""
{test_name}
    [Documentation]    {test_description}
    [Tags]             functional
    
    # Test Steps
    Log Test Info      Starting test: {test_name}
    
    # Add your test steps here
    Log    Test case: {test_name}
    Log    Description: {test_description}
    
    # Verification
    Log Test Info      Test completed successfully
"""
    
    def get_custom_keywords_template(self, resource_name: str) -> str:
        """Generate custom keywords resource file"""
        return f"""*** Settings ***
Documentation    {resource_name.replace('_', ' ').title()} Keywords
...              Custom keywords for specific functionality
Library          PlaywrightLibrary
Library          Collections

*** Keywords ***
Wait And Click Element
    [Documentation]    Wait for element to be clickable and click it
    [Arguments]    ${{locator}}    ${{timeout}}=30s
    Wait Until Element Is Enabled    ${{locator}}    ${{timeout}}
    Click Element    ${{locator}}

Input Text And Verify
    [Documentation]    Input text and verify it was entered correctly
    [Arguments]    ${{locator}}    ${{text}}
    Input Text    ${{locator}}    ${{text}}
    ${{entered_text}}=    Get Value    ${{locator}}
    Should Be Equal    ${{entered_text}}    ${{text}}

Take Screenshot With Timestamp
    [Documentation]    Take screenshot with timestamp in filename
    ${{timestamp}}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    Capture Page Screenshot    screenshot_${{timestamp}}.png

Verify Page Title Contains
    [Documentation]    Verify page title contains expected text
    [Arguments]    ${{expected_text}}
    ${{title}}=    Get Title
    Should Contain    ${{title}}    ${{expected_text}}

Wait For Page To Load
    [Documentation]    Wait for page to fully load
    [Arguments]    ${{timeout}}=30s
    Wait Until Page Contains Element    css=body    ${{timeout}}
    Wait For Condition    return document.readyState === 'complete'    ${{timeout}}

Handle Alert If Present
    [Documentation]    Handle alert if it appears
    ${{alert_present}}=    Run Keyword And Return Status    Alert Should Be Present
    Run Keyword If    ${{alert_present}}    Handle Alert    ACCEPT
"""
    
    def get_custom_variables_template(self, resource_name: str) -> str:
        """Generate custom variables resource file"""
        return f"""*** Variables ***
# {resource_name.replace('_', ' ').title()} Variables
# Custom variables for specific functionality

# Timeouts
${{DEFAULT_TIMEOUT}}        30s
${{SHORT_TIMEOUT}}          5s
${{LONG_TIMEOUT}}           60s

# Test Data
${{TEST_DATA_FILE}}         test_data.xlsx
${{CONFIG_FILE}}            config.yaml

# Custom Locators
${{CUSTOM_BUTTON}}          css=.custom-button
${{CUSTOM_INPUT}}           id=custom-input
${{CUSTOM_DROPDOWN}}        css=select.custom-dropdown
${{CUSTOM_CHECKBOX}}        css=input[type='checkbox'].custom

# Messages
${{SUCCESS_MESSAGE}}        Operation completed successfully
${{ERROR_MESSAGE}}          An error occurred
${{LOADING_MESSAGE}}        Loading...

# Colors (for validation)
${{PRIMARY_COLOR}}          #007bff
${{SUCCESS_COLOR}}          #28a745
${{WARNING_COLOR}}          #ffc107
${{ERROR_COLOR}}            #dc3545

# File Paths
${{DOWNLOAD_PATH}}          downloads/
${{UPLOAD_PATH}}            test_files/
${{REPORTS_PATH}}           reports/

# Custom Test Settings
&{{BROWSER_OPTIONS}}        add_argument=--disable-dev-shm-usage    add_argument=--no-sandbox
@{{VALID_FILE_TYPES}}       .pdf    .docx    .xlsx    .png    .jpg
"""
    
    def get_generic_resource_template(self, resource_name: str, resource_type: str) -> str:
        """Generate generic resource file template"""
        return f"""*** Settings ***
Documentation    {resource_name.replace('_', ' ').title()} Resource
...              Generic {resource_type} resource file
Library          PlaywrightLibrary

*** Variables ***
# {resource_name.replace('_', ' ').title()} Variables
${{RESOURCE_NAME}}          {resource_name}
${{RESOURCE_TYPE}}          {resource_type}

*** Keywords ***
{resource_name.replace('_', ' ').title()} Setup
    [Documentation]    Setup keyword for {resource_name}
    Log    Setting up {resource_name}

{resource_name.replace('_', ' ').title()} Teardown
    [Documentation]    Teardown keyword for {resource_name}
    Log    Tearing down {resource_name}

Verify {resource_name.replace('_', ' ').title()} Function
    [Documentation]    Verify main function of {resource_name}
    Log    Verifying {resource_name} functionality
    # Add your verification steps here
""" 