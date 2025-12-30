"""JIRA Test Automation MCP Server using FastMCP."""

from mcp.server.fastmcp import FastMCP
from .jira_service import JiraService
from .test_generator import TestGeneratorService

# Initialize FastMCP server
mcp = FastMCP("JIRA Test Automation")

# Initialize services
jira_service = JiraService()
test_generator = TestGeneratorService()


@mcp.tool()
async def fetch_jira_ticket(ticket_id: str) -> dict:
    """
    Fetch JIRA ticket information by ID or key.
    
    Args:
        ticket_id: JIRA ticket ID or key (e.g., PROJ-123)
    
    Returns:
        Complete ticket information including description, acceptance criteria, discussions, and metadata
    """
    return await jira_service.get_ticket_with_discussions(ticket_id)


@mcp.tool()
async def analyze_ticket_requirements(ticket_id: str) -> dict:
    """
    Analyze JIRA ticket to extract test scenarios and requirements.
    
    Args:
        ticket_id: JIRA ticket ID or key
    
    Returns:
        Analysis containing test scenarios, estimated test count, and complexity
    """
    ticket = await jira_service.get_ticket_with_discussions(ticket_id)
    return await test_generator.analyze_requirements(ticket)


@mcp.tool()
async def generate_test_scripts(
    ticket_id: str,
    language: str = "java",
    output_path: str | None = None,
) -> dict:
    """
    Generate Selenium + TestNG + Cucumber test scripts from JIRA ticket.
    
    Args:
        ticket_id: JIRA ticket ID or key
        language: Programming language for test scripts (java or python)
        output_path: Output directory path (default: ./generated-tests)
    
    Returns:
        Result containing list of generated files and success message
    """
    ticket = await jira_service.get_ticket_with_discussions(ticket_id)
    
    if language not in ["java", "python"]:
        return {
            "success": False,
            "message": f"Unsupported language: {language}. Use 'java' or 'python'",
        }
    
    return await test_generator.generate_tests(ticket, language, output_path)


@mcp.tool()
async def search_jira_tickets(jql: str, max_results: int = 10) -> dict:
    """
    Search JIRA tickets using JQL (JIRA Query Language).
    
    Args:
        jql: JQL query string (e.g., "project = PROJ AND status = Open")
        max_results: Maximum number of results to return
    
    Returns:
        Search results with matching tickets
    """
    return await jira_service.search_tickets(jql, max_results)


@mcp.tool()
async def generate_gherkin_features(
    ticket_id: str,
    output_path: str | None = None,
) -> dict:
    """
    Generate Cucumber Gherkin feature files from JIRA ticket.
    
    Args:
        ticket_id: JIRA ticket ID or key
        output_path: Output directory for feature files
    
    Returns:
        Generated feature file path and content
    """
    ticket = await jira_service.get_ticket_with_discussions(ticket_id)
    return await test_generator.generate_gherkin_features(ticket, output_path)


@mcp.tool()
async def generate_manual_test_plans(
    ticket_id: str,
    output_path: str | None = None,
) -> dict:
    """
    Generate comprehensive manual test plan documents from JIRA ticket.
    Creates detailed test plans with 100% coverage including positive, negative,
    boundary, security, performance, and integration test scenarios.
    
    Args:
        ticket_id: JIRA ticket ID or key
        output_path: Output directory for test plan files (default: ./generated-tests)
    
    Returns:
        Result containing list of generated test plan files
    """
    ticket = await jira_service.get_ticket_with_discussions(ticket_id)
    analysis = await test_generator.analyze_requirements(ticket)
    
    from pathlib import Path
    output_dir = Path(output_path or test_generator.output_dir) / ticket_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate only manual test plans
    test_plan_files = test_generator._generate_manual_test_plans(
        ticket, analysis, output_dir
    )
    
    return {
        "success": True,
        "files": test_plan_files,
        "message": f"Generated {len(test_plan_files)} manual test plan files for {ticket_id}",
        "test_count": len(test_plan_files),
    }


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

