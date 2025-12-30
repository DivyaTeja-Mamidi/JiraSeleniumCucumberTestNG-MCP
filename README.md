# JIRA Test Automation MCP Server

An MCP (Model Context Protocol) server using **FastMCP** that integrates with JIRA to automatically analyze tickets and generate comprehensive Selenium + TestNG + Cucumber test automation scripts with 100% coverage.

## Why FastMCP?

This project uses FastMCP for clean, pythonic MCP server development:

✅ **Decorator-based tools** - Simple `@mcp.tool()` decorator  
✅ **Automatic type inference** - Python type hints → MCP schemas  
✅ **Built-in documentation** - Docstrings → tool descriptions  
✅ **Less boilerplate** - 50% less code than raw SDK  
✅ **Modern Python** - async/await, type hints, pathlib  

## Features

### 🎯 Core Capabilities

- **JIRA Integration**: Fetch and analyze JIRA tickets using REST API
- **Requirement Analysis**: Extract test scenarios from ticket descriptions and acceptance criteria
- **Test Generation**: Generate complete test automation suites including:
  - Gherkin feature files (BDD format)
  - Step definitions (Java or Python)
  - Test runners with TestNG
  - Maven/pip configuration files
  - TestNG XML suite configuration
- **JQL Search**: Search for tickets using JIRA Query Language
- **Multi-Language Support**: Generate tests in Java or Python

### 🛠️ MCP Tools

The server exposes 5 tools via FastMCP decorators:

```python
@mcp.tool()
async def fetch_jira_ticket(ticket_id: str) -> dict:
    """Fetch JIRA ticket by ID or key"""

@mcp.tool()
async def analyze_ticket_requirements(ticket_id: str) -> dict:
    """Extract test scenarios from ticket"""

@mcp.tool()
async def generate_test_scripts(ticket_id: str, language: str = "java", ...) -> dict:
    """Generate complete Selenium+TestNG+Cucumber suite"""

@mcp.tool()
async def search_jira_tickets(jql: str, max_results: int = 10) -> dict:
    """Search tickets using JQL"""

@mcp.tool()
async def generate_gherkin_features(ticket_id: str, ...) -> dict:
    """Generate BDD-style Gherkin feature files"""
```

## Installation

### Prerequisites

- Python 3.10+ 
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- JIRA account with API access
- VS Code with GitHub Copilot (for MCP integration)

### Setup Steps

1. **Clone or navigate to the project directory**:
   ```bash
   cd JIRA_TestAutomation
   ```

2. **Install uv** (if not already installed):
   ```bash
   # Windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies**:
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   
   Create a `.env` file in the project root:
   ```env
   JIRA_BASE_URL=https://your-domain.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your_jira_api_token_here
   OUTPUT_DIRECTORY=./generated-tests
   ```

   **Get your JIRA API token**:
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Click "Create API token"
   - Give it a name and copy the token

## Configuration for VS Code

The project includes an MCP configuration file at `.vscode/mcp.json`. Update it with your JIRA credentials:

```json
{
  "mcpServers": {
    "jira-testautomation": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "c:\\Users\\dsmamidi\\JIRA_TestAutomation",
        "run",
        "jira-mcp"
      ],
      "env": {
        "JIRA_BASE_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

## Usage

### Using with VS Code GitHub Copilot

Once configured, you can use the MCP server with GitHub Copilot in VS Code:

1. Open VS Code with GitHub Copilot installed
2. The MCP server will be available through the mcp.json configuration
3. Use Copilot chat to interact with JIRA:

**Example prompts**:
- "Fetch JIRA ticket PROJ-123"
- "Analyze test requirements for PROJ-456"
- "Generate test scripts for PROJ-789 in Java"
- "Search for all open bugs in my project"
- "Generate Gherkin features for PROJ-321"

### Direct Usage (CLI)

You can also run the server directly for testing:

```bash
# Using uv
uv run jira-mcp

# Or using Python directly
python -m jira_mcp.server
```

## Generated Test Structure

When you generate tests for a JIRA ticket, the following structure is created:

```
generated-tests/
└── PROJ-123/
    ├── PROJ-123.feature          # Gherkin feature file
    ├── StepDefinitions.java      # Step implementations
    ├── TestRunner.java           # TestNG runner
    ├── testng.xml               # TestNG configuration
    ├── pom.xml                  # Maven configuration
    └── README.md                # Test documentation
```

### Example Feature File

```gherkin
Feature: User Login Functionality
  As a tester
  I want to test PROJ-123
  So that the functionality works as expected

  Scenario: Successful login with valid credentials
    Given User is on the login page
    When User enters valid username and password
    Then User should be redirected to dashboard
```

## Test Generation Process

1. **Ticket Fetching**: Retrieves complete ticket data from JIRA API
2. **Requirement Analysis**: 
   - Extracts acceptance criteria
   - Identifies Given-When-Then patterns
   - Generates test scenarios
3. **Test Script Generation**:
   - Creates Gherkin feature files
   - Generates step definitions with Selenium
   - Configures TestNG runners
   - Sets up project dependencies

## Framework Stack

- **FastMCP**: Pythonic MCP server framework
- **JIRA API**: REST API v3 for ticket management
- **Selenium**: Web automation framework
- **TestNG**: Test execution framework
- **Cucumber**: BDD test framework
- **Python 3.10+**: Modern Python with type hints

## Development

### Project Structure

```
JIRA_TestAutomation/
├── jira_mcp/
│   ├── __init__.py
│   ├── server.py              # FastMCP server with @tool decorators
│   ├── jira_service.py        # JIRA API integration
│   └── test_generator.py     # Test generation logic
├── .vscode/
│   └── mcp.json              # VS Code MCP configuration
├── .github/
│   └── copilot-instructions.md
├── pyproject.toml            # Python project config
├── requirements.txt          # Dependencies
└── .env.example
```

### Running in Development

```bash
# Install in editable mode
uv pip install -e .

# Run the server
uv run jira-mcp

# Or directly
python -m jira_mcp.server
```

## Code Comparison: FastMCP vs Raw SDK

### FastMCP (This Project) ✨
```python
@mcp.tool()
async def fetch_jira_ticket(ticket_id: str) -> dict:
    """Fetch JIRA ticket by ID or key"""
    return await jira_service.fetch_ticket(ticket_id)
```

### Raw TypeScript SDK ❌
```typescript
server.registerTool(
  "fetch_jira_ticket",
  {
    title: "Fetch JIRA Ticket",
    description: "Retrieve JIRA ticket information by ticket ID or key",
    inputSchema: {
      ticketId: z.string().describe("JIRA ticket ID or key (e.g., PROJ-123)"),
    },
  },
  async ({ ticketId }) => {
    try {
      const ticket = await jiraService.fetchTicket(ticketId);
      return {
        content: [{ type: "text", text: JSON.stringify(ticket, null, 2) }],
      };
    } catch (error) {
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
        isError: true,
      };
    }
  }
);
```

**FastMCP wins**: 3 lines vs 24 lines! 🎉

## Troubleshooting

### Common Issues

**JIRA Authentication Failed**:
- Verify your JIRA_BASE_URL is correct
- Ensure JIRA_EMAIL matches your Atlassian account
- Check that JIRA_API_TOKEN is valid and not expired

**Module Not Found Errors**:
- Run `uv sync` to install dependencies
- Ensure Python 3.10+ is installed

**Permission Issues**:
- Ensure you have write permissions to the output directory
- Check JIRA API token has required permissions (read issues)

## Security Notes

- Never commit your `.env` file or JIRA API tokens to version control
- Use environment variables for sensitive information
- Rotate API tokens periodically
- Limit API token permissions to only what's needed

## Resources

- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Specification](https://modelcontextprotocol.io/specification/latest)
- [JIRA REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [TestNG Documentation](https://testng.org/doc/)
- [Cucumber Documentation](https://cucumber.io/docs/cucumber/)

## License

ISC

## Features

### 🎯 Core Capabilities

- **JIRA Integration**: Fetch and analyze JIRA tickets using REST API
- **Requirement Analysis**: Extract test scenarios from ticket descriptions and acceptance criteria
- **Test Generation**: Generate complete test automation suites including:
  - Gherkin feature files (BDD format)
  - Step definitions (Java or Python)
  - Test runners with TestNG
  - Maven/pip configuration files
  - TestNG XML suite configuration
- **JQL Search**: Search for tickets using JIRA Query Language
- **Multi-Language Support**: Generate tests in Java or Python

### 🛠️ MCP Tools

The server exposes the following tools:

1. **fetch_jira_ticket** - Retrieve complete ticket information by ID/key
2. **analyze_ticket_requirements** - Extract and analyze test scenarios from tickets
3. **generate_test_scripts** - Generate complete Selenium+TestNG+Cucumber test suite
4. **search_jira_tickets** - Search tickets using JQL queries
5. **generate_gherkin_features** - Generate BDD-style Gherkin feature files

## Installation

### Prerequisites

- Node.js 16+ and npm
- JIRA account with API access
- VS Code (for MCP integration)

### Setup Steps

1. **Clone or navigate to the project directory**:
   \`\`\`bash
   cd JIRA_TestAutomation
   \`\`\`

2. **Install dependencies**:
   \`\`\`bash
   npm install
   \`\`\`

3. **Configure environment variables**:
   
   Create a \`.env\` file in the project root:
   \`\`\`env
   JIRA_BASE_URL=https://your-domain.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your_jira_api_token_here
   OUTPUT_DIRECTORY=./generated-tests
   \`\`\`

   **Get your JIRA API token**:
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Click "Create API token"
   - Give it a name and copy the token

4. **Build the project**:
   \`\`\`bash
   npm run build
   \`\`\`

## Configuration for VS Code

The project includes an MCP configuration file at \`.vscode/mcp.json\`. Update it with your JIRA credentials:

\`\`\`json
{
  "mcpServers": {
    "jira-testautomation": {
      "type": "stdio",
      "command": "node",
      "args": ["c:\\\\Users\\\\dsmamidi\\\\JIRA_TestAutomation\\\\build\\\\index.js"],
      "env": {
        "JIRA_BASE_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
\`\`\`

## Usage

### Using with VS Code GitHub Copilot

Once configured, you can use the MCP server with GitHub Copilot in VS Code:

1. Open VS Code with GitHub Copilot installed
2. The MCP server will be available through the mcp.json configuration
3. Use Copilot chat to interact with JIRA:

**Example prompts**:
- "Fetch JIRA ticket PROJ-123"
- "Analyze test requirements for PROJ-456"
- "Generate test scripts for PROJ-789 in Java"
- "Search for all open bugs in my project"
- "Generate Gherkin features for PROJ-321"

### Direct Usage (CLI)

You can also run the server directly for testing:

\`\`\`bash
npm run dev
\`\`\`

## Generated Test Structure

When you generate tests for a JIRA ticket, the following structure is created:

\`\`\`
generated-tests/
└── PROJ-123/
    ├── PROJ-123.feature          # Gherkin feature file
    ├── StepDefinitions.java      # Step implementations
    ├── TestRunner.java           # TestNG runner
    ├── testng.xml               # TestNG configuration
    ├── pom.xml                  # Maven configuration
    └── README.md                # Test documentation
\`\`\`

### Example Feature File

\`\`\`gherkin
Feature: User Login Functionality
  As a tester
  I want to test PROJ-123
  So that the functionality works as expected

  Scenario: Successful login with valid credentials
    Given User is on the login page
    When User enters valid username and password
    Then User should be redirected to dashboard
\`\`\`

## Test Generation Process

1. **Ticket Fetching**: Retrieves complete ticket data from JIRA API
2. **Requirement Analysis**: 
   - Extracts acceptance criteria
   - Identifies Given-When-Then patterns
   - Generates test scenarios
3. **Test Script Generation**:
   - Creates Gherkin feature files
   - Generates step definitions with Selenium
   - Configures TestNG runners
   - Sets up project dependencies

## Framework Stack

- **MCP SDK**: Model Context Protocol integration
- **JIRA API**: REST API v3 for ticket management
- **Selenium**: Web automation framework
- **TestNG**: Test execution framework
- **Cucumber**: BDD test framework
- **TypeScript**: Server implementation language

## Development

### Project Structure

\`\`\`
JIRA_TestAutomation/
├── src/
│   ├── index.ts                      # MCP server entry point
│   └── services/
│       ├── jira.service.ts           # JIRA API integration
│       └── test-generator.service.ts # Test generation logic
├── build/                            # Compiled JavaScript
├── .vscode/
│   └── mcp.json                     # VS Code MCP configuration
├── .github/
│   └── copilot-instructions.md      # Copilot guidelines
├── package.json
├── tsconfig.json
└── .env.example
\`\`\`

### Building from Source

\`\`\`bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Build for production
npm run build

# Start server
npm start
\`\`\`

## Troubleshooting

### Common Issues

**JIRA Authentication Failed**:
- Verify your JIRA_BASE_URL is correct
- Ensure JIRA_EMAIL matches your Atlassian account
- Check that JIRA_API_TOKEN is valid and not expired

**Module Not Found Errors**:
- Run \`npm install\` to ensure all dependencies are installed
- Check that TypeScript compilation succeeded with \`npm run build\`

**Permission Issues**:
- Ensure you have write permissions to the output directory
- Check JIRA API token has required permissions (read issues)

## Security Notes

- Never commit your \`.env\` file or JIRA API tokens to version control
- Use environment variables for sensitive information
- Rotate API tokens periodically
- Limit API token permissions to only what's needed

## Contributing

Feel free to enhance the test generation logic, add new patterns for requirement extraction, or extend support for additional test frameworks.

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [JIRA REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [TestNG Documentation](https://testng.org/doc/)
- [Cucumber Documentation](https://cucumber.io/docs/cucumber/)

## License

ISC

## Author

Created for automated test generation from JIRA tickets using MCP.
