# Copilot Instructions for JIRA Test Automation MCP Server

This project creates an MCP server that integrates with JIRA to automatically generate Selenium + TestNG + Cucumber test automation scripts with 100% coverage.

## Project Requirements

- Node.js/TypeScript MCP server
- JIRA API integration for ticket fetching
- AI-powered requirement analysis
- Test script generation engine (Selenium + TestNG + Cucumber)
- Support for Gherkin/BDD format

## Development Guidelines

1. Follow MCP specification requirements from https://modelcontextprotocol.io
2. Use TypeScript SDK for MCP server implementation
3. Implement secure JIRA credential management
4. Generate comprehensive test scripts based on ticket requirements
5. Support both STDIO and SSE transport protocols

## Configuration

- Store JIRA credentials in environment variables (.env file)
- Configure MCP server in mcp.json for VS Code integration
- Follow MCP best practices for tool registration

## References

- MCP TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- MCP Specification: https://modelcontextprotocol.io/specification/latest
- MCP Server Documentation: https://modelcontextprotocol.io/docs/develop/build-server
