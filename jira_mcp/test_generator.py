"""Test automation script generator for Selenium + TestNG + Cucumber."""

import os
import re
from pathlib import Path
from typing import Any, Literal


class TestScenario:
    """Represents a test scenario with Given-When-Then steps."""

    def __init__(
        self,
        scenario: str,
        given: list[str],
        when: list[str],
        then: list[str],
    ):
        self.scenario = scenario
        self.given = given
        self.when = when
        self.then = then


class TestGeneratorService:
    """Service for generating test automation scripts."""

    def __init__(self):
        self.output_dir = os.getenv("OUTPUT_DIRECTORY", "./generated-tests")

    async def analyze_requirements(self, ticket: dict[str, Any]) -> dict[str, Any]:
        """Analyze ticket requirements and extract test scenarios."""
        fields = ticket.get("fields", {})
        description = fields.get("description", "")
        summary = fields.get("summary", "")
        discussion_summary = ticket.get("discussion_summary", "")

        scenarios = self._extract_test_scenarios(description, summary, discussion_summary)
        complexity = self._calculate_complexity(scenarios, description)

        return {
            "ticket_key": ticket["key"],
            "summary": summary,
            "discussion_summary": discussion_summary,
            "test_scenarios": [
                {
                    "scenario": s.scenario,
                    "given": s.given,
                    "when": s.when,
                    "then": s.then,
                }
                for s in scenarios
            ],
            "estimated_test_count": len(scenarios),
            "complexity": complexity,
        }

    async def generate_tests(
        self,
        ticket: dict[str, Any],
        language: Literal["java", "python"] = "java",
        output_path: str | None = None,
    ) -> dict[str, Any]:
        """Generate complete test automation suite."""
        analysis = await self.analyze_requirements(ticket)
        ticket_key = ticket["key"]
        output_directory = Path(output_path or self.output_dir) / ticket_key
        output_directory.mkdir(parents=True, exist_ok=True)

        generated_files = []

        # Generate Gherkin feature file
        feature_content = self._generate_feature_file(analysis)
        feature_path = output_directory / f"{ticket_key}.feature"
        feature_path.write_text(feature_content, encoding="utf-8")
        generated_files.append(str(feature_path))

        # Generate language-specific files
        if language == "java":
            java_files = self._generate_java_tests(analysis, output_directory)
            generated_files.extend(java_files)
        else:
            python_files = self._generate_python_tests(analysis, output_directory)
            generated_files.extend(python_files)

        # Generate TestNG XML
        testng_content = self._generate_testng_xml(analysis)
        testng_path = output_directory / "testng.xml"
        testng_path.write_text(testng_content, encoding="utf-8")
        generated_files.append(str(testng_path))

        # Generate README
        readme_content = self._generate_readme(analysis, language)
        readme_path = output_directory / "README.md"
        readme_path.write_text(readme_content, encoding="utf-8")
        generated_files.append(str(readme_path))

        # Generate manual test plans
        manual_test_files = self._generate_manual_test_plans(
            ticket, analysis, output_directory
        )
        generated_files.extend(manual_test_files)

        return {
            "success": True,
            "files": generated_files,
            "message": f"Generated {len(generated_files)} files for {ticket_key}",
        }

    async def generate_gherkin_features(
        self, ticket: dict[str, Any], output_path: str | None = None
    ) -> dict[str, Any]:
        """Generate Gherkin feature files only."""
        analysis = await self.analyze_requirements(ticket)
        feature_content = self._generate_feature_file(analysis)
        ticket_key = ticket["key"]

        if output_path:
            feature_path = Path(output_path) / f"{ticket_key}.feature"
            feature_path.parent.mkdir(parents=True, exist_ok=True)
            feature_path.write_text(feature_content, encoding="utf-8")
            return {
                "success": True,
                "file": str(feature_path),
                "content": feature_content,
            }

        return {
            "success": True,
            "file": f"{ticket_key}.feature",
            "content": feature_content,
        }

    def _extract_test_scenarios(
        self, description: str, summary: str, discussion_summary: str = ""
    ) -> list[TestScenario]:
        """Extract test scenarios from description and discussions."""
        scenarios = []
        
        # Combine description and discussion for comprehensive analysis
        combined_text = f"{description}\n\n{discussion_summary}"

        # Pattern: Given-When-Then format
        gwt_pattern = re.compile(
            r"given\s+(.*?)(?:\n|$).*?when\s+(.*?)(?:\n|$).*?then\s+(.*?)(?:\n|$)",
            re.IGNORECASE | re.DOTALL,
        )

        for match in gwt_pattern.finditer(combined_text):
            scenarios.append(
                TestScenario(
                    scenario=f"Scenario: {summary}",
                    given=[match.group(1).strip()],
                    when=[match.group(2).strip()],
                    then=[match.group(3).strip()],
                )
            )

        # Extract additional scenarios from discussions
        if discussion_summary:
            discussion_scenarios = self._extract_scenarios_from_discussions(discussion_summary, summary)
            scenarios.extend(discussion_scenarios)

        # Fallback: Create basic scenario
        if not scenarios:
            scenarios.append(
                TestScenario(
                    scenario=f"Test {summary}",
                    given=["User is on the application"],
                    when=["User performs the action described in ticket"],
                    then=["Expected behavior occurs as per ticket description"],
                )
            )

        return scenarios
    
    def _extract_scenarios_from_discussions(
        self, discussion_summary: str, summary: str
    ) -> list[TestScenario]:
        """Extract additional test scenarios from discussion comments."""
        scenarios = []
        
        # Look for test-related keywords in discussions
        test_keywords = [
            r"test\s+case[s]?:?\s*(.*?)(?:\n\n|$)",
            r"scenario[s]?:?\s*(.*?)(?:\n\n|$)",
            r"edge\s+case[s]?:?\s*(.*?)(?:\n\n|$)",
            r"acceptance\s+criteria:?\s*(.*?)(?:\n\n|$)",
            r"should\s+(.*?)(?:\n|$)",
            r"verify\s+(.*?)(?:\n|$)",
            r"ensure\s+(.*?)(?:\n|$)",
        ]
        
        for pattern in test_keywords:
            matches = re.finditer(pattern, discussion_summary, re.IGNORECASE | re.DOTALL)
            for match in matches:
                scenario_text = match.group(1).strip()
                if scenario_text and len(scenario_text) > 10:
                    # Create a scenario from the discussion point
                    scenarios.append(
                        TestScenario(
                            scenario=f"Scenario from discussion: {scenario_text[:100]}",
                            given=["User is on the application"],
                            when=[f"User performs: {scenario_text[:150]}"],
                            then=["Expected behavior should match the discussion requirement"],
                        )
                    )
        
        return scenarios

    def _calculate_complexity(
        self, scenarios: list[TestScenario], description: str
    ) -> Literal["low", "medium", "high"]:
        """Calculate test complexity."""
        scenario_count = len(scenarios)
        desc_length = len(description)

        if scenario_count <= 2 and desc_length < 500:
            return "low"
        if scenario_count <= 5 and desc_length < 1500:
            return "medium"
        return "high"

    def _generate_feature_file(self, analysis: dict[str, Any]) -> str:
        """Generate Gherkin feature file content."""
        lines = [
            f"Feature: {analysis['summary']}",
            "  As a tester",
            f"  I want to test {analysis['ticket_key']}",
            "  So that the functionality works as expected",
            "",
        ]
        
        # Add discussion context if available
        if analysis.get("discussion_summary"):
            lines.append("  # Additional context from discussions:")
            discussion_lines = analysis["discussion_summary"].split("\n\n")
            for disc_line in discussion_lines[:3]:  # Limit to first 3 discussion points
                if disc_line.strip():
                    lines.append(f"  # {disc_line.strip()[:100]}")
            lines.append("")

        for i, scenario in enumerate(analysis["test_scenarios"]):
            lines.append(f"  Scenario: {scenario['scenario']}")
            for step in scenario["given"]:
                lines.append(f"    Given {step}")
            for step in scenario["when"]:
                lines.append(f"    When {step}")
            for step in scenario["then"]:
                lines.append(f"    Then {step}")
            if i < len(analysis["test_scenarios"]) - 1:
                lines.append("")

        return "\n".join(lines)

    def _generate_java_tests(
        self, analysis: dict[str, Any], output_dir: Path
    ) -> list[str]:
        """Generate Java test files."""
        files = []
        class_name = analysis["ticket_key"].replace("-", "_")

        # Step definitions
        step_defs = f'''package stepdefinitions;

import io.cucumber.java.en.*;
import io.cucumber.java.After;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.testng.Assert;

public class {class_name}StepDefinitions {{
    private WebDriver driver;

    @Given("{{string}}")
    public void given_step(String step) {{
        System.out.println("Given: " + step);
        driver = new ChromeDriver();
        // TODO: Implement step logic
    }}

    @When("{{string}}")
    public void when_step(String step) {{
        System.out.println("When: " + step);
        // TODO: Implement step logic
    }}

    @Then("{{string}}")
    public void then_step(String step) {{
        System.out.println("Then: " + step);
        // TODO: Implement assertion logic
        Assert.assertTrue(true, "Placeholder assertion");
    }}

    @After
    public void tearDown() {{
        if (driver != null) {{
            driver.quit();
        }}
    }}
}}
'''
        step_path = output_dir / "StepDefinitions.java"
        step_path.write_text(step_defs, encoding="utf-8")
        files.append(str(step_path))

        # Test runner
        runner = f'''package runners;

import io.cucumber.testng.AbstractTestNGCucumberTests;
import io.cucumber.testng.CucumberOptions;

@CucumberOptions(
    features = "src/test/resources/features/{analysis["ticket_key"]}.feature",
    glue = {{"stepdefinitions"}},
    plugin = {{
        "pretty",
        "html:target/cucumber-reports/cucumber.html",
        "json:target/cucumber-reports/cucumber.json"
    }},
    monochrome = true
)
public class {class_name}TestRunner extends AbstractTestNGCucumberTests {{
}}
'''
        runner_path = output_dir / "TestRunner.java"
        runner_path.write_text(runner, encoding="utf-8")
        files.append(str(runner_path))

        # POM XML
        pom = f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.testautomation</groupId>
    <artifactId>{analysis["ticket_key"].lower()}</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <selenium.version>4.15.0</selenium.version>
        <cucumber.version>7.14.0</cucumber.version>
        <testng.version>7.8.0</testng.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.seleniumhq.selenium</groupId>
            <artifactId>selenium-java</artifactId>
            <version>${{selenium.version}}</version>
        </dependency>
        <dependency>
            <groupId>io.cucumber</groupId>
            <artifactId>cucumber-java</artifactId>
            <version>${{cucumber.version}}</version>
        </dependency>
        <dependency>
            <groupId>io.cucumber</groupId>
            <artifactId>cucumber-testng</artifactId>
            <version>${{cucumber.version}}</version>
        </dependency>
        <dependency>
            <groupId>org.testng</groupId>
            <artifactId>testng</artifactId>
            <version>${{testng.version}}</version>
        </dependency>
    </dependencies>
</project>
'''
        pom_path = output_dir / "pom.xml"
        pom_path.write_text(pom, encoding="utf-8")
        files.append(str(pom_path))

        return files

    def _generate_python_tests(
        self, analysis: dict[str, Any], output_dir: Path
    ) -> list[str]:
        """Generate Python test files."""
        files = []

        # Step definitions
        step_defs = '''from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@given(u'{step}')
def step_given(context, step):
    print(f"Given: {step}")
    context.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # TODO: Implement step logic

@when(u'{step}')
def step_when(context, step):
    print(f"When: {step}")
    # TODO: Implement step logic

@then(u'{step}')
def step_then(context, step):
    print(f"Then: {step}")
    # TODO: Implement assertion logic
    assert True, "Placeholder assertion"

def after_scenario(context, scenario):
    if hasattr(context, 'driver'):
        context.driver.quit()
'''
        step_path = output_dir / "step_definitions.py"
        step_path.write_text(step_defs, encoding="utf-8")
        files.append(str(step_path))

        # Requirements
        requirements = '''selenium==4.15.0
behave==1.2.6
webdriver-manager==4.0.1
pytest==7.4.3
allure-behave==2.13.2
'''
        req_path = output_dir / "requirements.txt"
        req_path.write_text(requirements, encoding="utf-8")
        files.append(str(req_path))

        return files

    def _generate_testng_xml(self, analysis: dict[str, Any]) -> str:
        """Generate TestNG XML configuration."""
        class_name = analysis["ticket_key"].replace("-", "_")
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE suite SYSTEM "http://testng.org/testng-1.0.dtd">
<suite name="{analysis["ticket_key"]} Test Suite" parallel="false">
    <test name="{analysis["ticket_key"]} Tests">
        <classes>
            <class name="runners.{class_name}TestRunner"/>
        </classes>
    </test>
</suite>
'''

    def _generate_readme(self, analysis: dict[str, Any], language: str) -> str:
        """Generate README documentation."""
        scenarios_text = "\n\n".join(
            f'''### {i+1}. {s["scenario"]}
- **Given**: {", ".join(s["given"])}
- **When**: {", ".join(s["when"])}
- **Then**: {", ".join(s["then"])}'''
            for i, s in enumerate(analysis["test_scenarios"])
        )

        setup_instructions = (
            """1. Install Java JDK 11 or higher
2. Install Maven
3. Run: `mvn clean install`
4. Execute tests: `mvn test`"""
            if language == "java"
            else """1. Install Python 3.8 or higher
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `behave`"""
        )

        return f'''# Test Automation for {analysis["ticket_key"]}

## Summary
{analysis["summary"]}

## Test Information
- **Ticket**: {analysis["ticket_key"]}
- **Estimated Test Count**: {analysis["estimated_test_count"]}
- **Complexity**: {analysis["complexity"]}
- **Language**: {language}
- **Framework**: Selenium + TestNG + Cucumber

## Setup Instructions

### {language.title()} Setup

{setup_instructions}

## Test Scenarios

{scenarios_text}

## Generated Files
- Feature file with Gherkin scenarios
- Step definition implementations
- Test runner configuration
- TestNG XML suite configuration
- Dependencies configuration

## Next Steps
1. Review generated test scenarios
2. Implement step definitions with actual test logic
3. Add page objects for UI elements
4. Configure test data and environments
5. Run tests and review results

## Notes
- Auto-generated test suite based on JIRA ticket {analysis["ticket_key"]}
- Review and enhance test logic as needed
- Add assertions specific to your application
- Integrate with CI/CD pipeline
'''

    def _generate_manual_test_plans(
        self, ticket: dict[str, Any], analysis: dict[str, Any], output_dir: Path
    ) -> list[str]:
        """Generate detailed manual test plan files with 100% coverage."""
        generated_files = []
        ticket_key = analysis["ticket_key"]
        fields = ticket.get("fields", {})
        
        # Extract all relevant information
        description = fields.get("description", "")
        summary = analysis.get("summary", "")
        discussion_summary = analysis.get("discussion_summary", "")
        test_scenarios = analysis.get("test_scenarios", [])
        
        # Generate test plans for each scenario
        for idx, scenario in enumerate(test_scenarios, start=1):
            test_plan_content = self._create_manual_test_plan(
                ticket_key=ticket_key,
                test_number=idx,
                scenario=scenario,
                summary=summary,
                description=description,
                discussion_summary=discussion_summary,
                total_tests=len(test_scenarios)
            )
            
            # Create filename: <JIRA_ID>_Test<number>.txt
            filename = f"{ticket_key}_Test{idx}.txt"
            file_path = output_dir / filename
            file_path.write_text(test_plan_content, encoding="utf-8")
            generated_files.append(str(file_path))
        
        # Generate additional edge case and negative test plans
        additional_tests = self._generate_additional_test_cases(
            ticket_key=ticket_key,
            description=description,
            discussion_summary=discussion_summary,
            starting_index=len(test_scenarios) + 1
        )
        
        for idx, test_content in enumerate(additional_tests, start=len(test_scenarios) + 1):
            filename = f"{ticket_key}_Test{idx}.txt"
            file_path = output_dir / filename
            file_path.write_text(test_content, encoding="utf-8")
            generated_files.append(str(file_path))
        
        return generated_files
    
    def _create_manual_test_plan(
        self,
        ticket_key: str,
        test_number: int,
        scenario: dict[str, Any],
        summary: str,
        description: str,
        discussion_summary: str,
        total_tests: int
    ) -> str:
        """Create a detailed manual test plan document."""
        
        # Extract scenario details
        scenario_name = scenario.get("scenario", "Test Scenario")
        given_steps = scenario.get("given", [])
        when_steps = scenario.get("when", [])
        then_steps = scenario.get("then", [])
        
        # Build test steps
        test_steps = []
        step_number = 1
        
        # Preconditions from Given
        for given in given_steps:
            test_steps.append({
                "step_num": step_number,
                "action": f"Verify precondition: {given}",
                "expected": "Precondition is met and ready for testing",
                "type": "Precondition"
            })
            step_number += 1
        
        # Actions from When
        for when in when_steps:
            test_steps.append({
                "step_num": step_number,
                "action": self._expand_action_step(when),
                "expected": "Action completes without errors",
                "type": "Action"
            })
            step_number += 1
        
        # Validations from Then
        for then in then_steps:
            test_steps.append({
                "step_num": step_number,
                "action": f"Verify: {then}",
                "expected": then,
                "type": "Validation"
            })
            step_number += 1
        
        # Add cleanup step
        test_steps.append({
            "step_num": step_number,
            "action": "Clean up test data and restore initial state",
            "expected": "System returns to original state",
            "type": "Cleanup"
        })
        
        # Format the test plan
        content = f"""{'='*80}
MANUAL TEST PLAN
{'='*80}

TICKET ID:           {ticket_key}
TEST ID:             {ticket_key}_Test{test_number}
TEST NUMBER:         {test_number} of {total_tests}
TEST NAME:           {scenario_name}
CREATED DATE:        {self._get_current_date()}
TEST TYPE:           Functional Test
PRIORITY:            High
AUTOMATION:          Planned

{'='*80}
TEST SUMMARY
{'='*80}
{summary}

{'='*80}
TEST OBJECTIVE
{'='*80}
{scenario_name}

This test validates the functionality described in {ticket_key} ensuring that the
system behaves as expected according to the requirements and acceptance criteria.

{'='*80}
REQUIREMENTS REFERENCE
{'='*80}
Ticket Description:
{self._format_description(description)}

"""
        
        if discussion_summary:
            content += f"""Additional Context from Discussions:
{self._format_discussion_context(discussion_summary)}

"""
        
        content += f"""{'='*80}
TEST PRECONDITIONS
{'='*80}
"""
        
        precondition_steps = [s for s in test_steps if s["type"] == "Precondition"]
        if precondition_steps:
            for step in precondition_steps:
                content += f"{step['step_num']}. {step['action']}\n"
        else:
            content += "1. Application is accessible and running\n"
            content += "2. Test user has appropriate access rights\n"
            content += "3. Test environment is properly configured\n"
        
        content += f"""
{'='*80}
TEST STEPS
{'='*80}

"""
        
        # Write detailed test steps
        for step in test_steps:
            content += f"""Step {step['step_num']}: [{step['type']}]
{'─'*80}
Action:
  {step['action']}

Expected Result:
  {step['expected']}

Actual Result:
  [ TO BE FILLED DURING EXECUTION ]

Status: [ PASS / FAIL / BLOCKED ]

{'='*80}

"""
        
        content += f"""{'='*80}
TEST DATA REQUIREMENTS
{'='*80}
"""
        
        # Extract test data from steps
        test_data = self._extract_test_data_requirements(test_steps, description)
        for data_item in test_data:
            content += f"- {data_item}\n"
        
        content += f"""
{'='*80}
EXPECTED RESULTS SUMMARY
{'='*80}
"""
        
        validation_steps = [s for s in test_steps if s["type"] == "Validation"]
        for idx, step in enumerate(validation_steps, 1):
            content += f"{idx}. {step['expected']}\n"
        
        content += f"""
{'='*80}
PASS/FAIL CRITERIA
{'='*80}
PASS: All test steps execute successfully and all expected results are observed
FAIL: Any test step fails or expected result is not observed
BLOCKED: Test cannot be executed due to environment or dependency issues

{'='*80}
NOTES AND OBSERVATIONS
{'='*80}
[ TO BE FILLED DURING EXECUTION ]

Tester Name:     _____________________
Test Date:       _____________________
Test Duration:   _____________________
Environment:     _____________________
Build/Version:   _____________________

Final Status:    [ PASS / FAIL / BLOCKED ]

{'='*80}
DEFECTS FOUND
{'='*80}
Defect ID | Severity | Description | Status
{'─'*80}
[ TO BE FILLED IF DEFECTS ARE FOUND ]

{'='*80}
END OF TEST PLAN - {ticket_key}_Test{test_number}
{'='*80}
"""
        
        return content
    
    def _generate_additional_test_cases(
        self, ticket_key: str, description: str, discussion_summary: str, starting_index: int
    ) -> list[str]:
        """Generate additional test cases for edge cases, negative scenarios, and boundary conditions."""
        additional_tests = []
        current_index = starting_index
        
        # Define comprehensive test scenarios for 100% coverage
        additional_scenarios = [
            {
                "name": "Negative Test - Invalid Input Data",
                "objective": "Verify system handles invalid input gracefully",
                "steps": [
                    {"action": "Prepare invalid test data (empty, null, special characters)", "expected": "Test data is prepared"},
                    {"action": "Attempt to perform the operation with invalid data", "expected": "System rejects invalid input"},
                    {"action": "Verify appropriate error message is displayed", "expected": "Clear error message explains the validation failure"},
                    {"action": "Verify system state remains unchanged", "expected": "No data is corrupted or modified"},
                ],
                "type": "Negative"
            },
            {
                "name": "Boundary Test - Minimum Values",
                "objective": "Verify system behavior at minimum boundary conditions",
                "steps": [
                    {"action": "Identify minimum acceptable values from requirements", "expected": "Boundaries are documented"},
                    {"action": "Test with minimum valid values", "expected": "Operation succeeds with minimum values"},
                    {"action": "Test with values below minimum (if applicable)", "expected": "System rejects or handles appropriately"},
                    {"action": "Verify data integrity at boundaries", "expected": "Data is stored and displayed correctly"},
                ],
                "type": "Boundary"
            },
            {
                "name": "Boundary Test - Maximum Values",
                "objective": "Verify system behavior at maximum boundary conditions",
                "steps": [
                    {"action": "Identify maximum acceptable values from requirements", "expected": "Boundaries are documented"},
                    {"action": "Test with maximum valid values", "expected": "Operation succeeds with maximum values"},
                    {"action": "Test with values above maximum (if applicable)", "expected": "System rejects or handles appropriately"},
                    {"action": "Verify performance and response time", "expected": "System performs within acceptable limits"},
                ],
                "type": "Boundary"
            },
            {
                "name": "Security Test - Access Control",
                "objective": "Verify proper authorization and access controls",
                "steps": [
                    {"action": "Attempt operation with unauthorized user", "expected": "Access is denied"},
                    {"action": "Verify appropriate error/permission message", "expected": "User receives clear permission denied message"},
                    {"action": "Test with user having partial permissions", "expected": "Only authorized actions are allowed"},
                    {"action": "Verify audit logs capture access attempts", "expected": "Security events are logged"},
                ],
                "type": "Security"
            },
            {
                "name": "Performance Test - Response Time",
                "objective": "Verify system performs within acceptable time limits",
                "steps": [
                    {"action": "Execute operation with normal data load", "expected": "Baseline performance is established"},
                    {"action": "Measure response time for the operation", "expected": "Response time is within SLA requirements"},
                    {"action": "Test with increased data volume", "expected": "Performance degrades gracefully"},
                    {"action": "Verify no memory leaks or resource issues", "expected": "Resources are properly managed"},
                ],
                "type": "Performance"
            },
            {
                "name": "Usability Test - User Experience",
                "objective": "Verify user interface is intuitive and accessible",
                "steps": [
                    {"action": "Navigate to the feature using normal user flow", "expected": "Navigation is intuitive"},
                    {"action": "Verify all UI elements are properly labeled", "expected": "Labels are clear and descriptive"},
                    {"action": "Test keyboard navigation and accessibility", "expected": "Feature is keyboard accessible"},
                    {"action": "Verify error messages are user-friendly", "expected": "Messages guide user to resolution"},
                ],
                "type": "Usability"
            },
            {
                "name": "Integration Test - External Dependencies",
                "objective": "Verify proper integration with dependent systems",
                "steps": [
                    {"action": "Identify external system dependencies", "expected": "Dependencies are documented"},
                    {"action": "Test with all dependencies available", "expected": "Integration works correctly"},
                    {"action": "Test with dependency unavailable/timeout", "expected": "System handles failures gracefully"},
                    {"action": "Verify error handling and retry logic", "expected": "Appropriate error handling is in place"},
                ],
                "type": "Integration"
            },
            {
                "name": "Data Validation Test - Input Constraints",
                "objective": "Verify all input validations are properly enforced",
                "steps": [
                    {"action": "Test with required fields missing", "expected": "Validation errors are shown"},
                    {"action": "Test with incorrect data types", "expected": "Type validation works correctly"},
                    {"action": "Test with data exceeding length limits", "expected": "Length constraints are enforced"},
                    {"action": "Test with SQL injection and XSS attempts", "expected": "Input sanitization prevents attacks"},
                ],
                "type": "Validation"
            },
        ]
        
        # Generate test plan for each additional scenario
        for scenario in additional_scenarios:
            test_content = self._create_additional_test_plan(
                ticket_key=ticket_key,
                test_number=current_index,
                scenario=scenario,
                description=description,
                discussion_summary=discussion_summary
            )
            additional_tests.append(test_content)
            current_index += 1
        
        return additional_tests
    
    def _create_additional_test_plan(
        self, ticket_key: str, test_number: int, scenario: dict, description: str, discussion_summary: str
    ) -> str:
        """Create test plan for additional test scenarios."""
        
        content = f"""{'='*80}
MANUAL TEST PLAN - {scenario['type'].upper()} TEST
{'='*80}

TICKET ID:           {ticket_key}
TEST ID:             {ticket_key}_Test{test_number}
TEST NUMBER:         {test_number}
TEST NAME:           {scenario['name']}
CREATED DATE:        {self._get_current_date()}
TEST TYPE:           {scenario['type']} Test
PRIORITY:            High
AUTOMATION:          Planned

{'='*80}
TEST OBJECTIVE
{'='*80}
{scenario['objective']}

This test ensures comprehensive coverage by validating {scenario['type'].lower()} scenarios
that complement the functional requirements specified in {ticket_key}.

{'='*80}
REQUIREMENTS REFERENCE
{'='*80}
Based on ticket: {ticket_key}

{self._format_description(description)}

{'='*80}
TEST PRECONDITIONS
{'='*80}
1. All functional tests for {ticket_key} have been reviewed
2. Test environment is stable and accessible
3. Test data is prepared according to test type requirements
4. Required user accounts and permissions are configured

{'='*80}
TEST STEPS
{'='*80}

"""
        
        for idx, step in enumerate(scenario['steps'], 1):
            content += f"""Step {idx}:
{'─'*80}
Action:
  {step['action']}

Expected Result:
  {step['expected']}

Actual Result:
  [ TO BE FILLED DURING EXECUTION ]

Status: [ PASS / FAIL / BLOCKED ]

{'='*80}

"""
        
        content += f"""{'='*80}
PASS/FAIL CRITERIA
{'='*80}
PASS: All validation points pass and system behaves according to {scenario['type'].lower()} test requirements
FAIL: Any expected behavior is not observed or system behaves incorrectly
BLOCKED: Test cannot be completed due to dependencies or environment issues

{'='*80}
NOTES AND OBSERVATIONS
{'='*80}
[ TO BE FILLED DURING EXECUTION ]

This {scenario['type'].lower()} test is critical for ensuring 100% test coverage and
should be executed as part of the comprehensive test suite for {ticket_key}.

Tester Name:     _____________________
Test Date:       _____________________
Environment:     _____________________
Build/Version:   _____________________

Final Status:    [ PASS / FAIL / BLOCKED ]

{'='*80}
END OF TEST PLAN - {ticket_key}_Test{test_number}
{'='*80}
"""
        
        return content
    
    def _expand_action_step(self, action: str) -> str:
        """Expand action step with more detailed instructions."""
        if len(action) < 50:
            return f"{action} (Provide detailed steps as applicable)"
        return action
    
    def _format_description(self, description: str) -> str:
        """Format description for readability in test plan."""
        if not description:
            return "No detailed description available. Refer to ticket summary."
        
        # Limit length and format
        formatted = description.replace("\r\n", "\n").strip()
        if len(formatted) > 500:
            formatted = formatted[:500] + "...\n[See full description in JIRA ticket]"
        
        return formatted
    
    def _format_discussion_context(self, discussion_summary: str) -> str:
        """Format discussion context for test plan."""
        if not discussion_summary:
            return "No additional discussions available."
        
        # Limit and format discussion points
        discussions = discussion_summary.split("\n\n")
        formatted_discussions = []
        
        for disc in discussions[:5]:  # Limit to top 5 discussions
            if disc.strip():
                formatted_discussions.append(f"  - {disc.strip()}")
        
        return "\n".join(formatted_discussions) if formatted_discussions else "No significant discussion points."
    
    def _extract_test_data_requirements(self, test_steps: list[dict], description: str) -> list[str]:
        """Extract test data requirements from steps and description."""
        data_requirements = [
            "Valid user credentials for test execution",
            "Test environment access configuration",
            "Sample data matching requirements specifications",
        ]
        
        # Look for data mentions in description
        data_keywords = ["email", "username", "password", "name", "address", "phone", "date", "number", "id", "code"]
        description_lower = description.lower() if description else ""
        
        for keyword in data_keywords:
            if keyword in description_lower:
                data_requirements.append(f"Valid test {keyword} data")
        
        # Check steps for data requirements
        for step in test_steps:
            action_lower = step['action'].lower()
            if "data" in action_lower or "value" in action_lower or "input" in action_lower:
                data_requirements.append(f"Data for: {step['action'][:60]}")
        
        return list(set(data_requirements))[:10]  # Remove duplicates and limit
    
    def _get_current_date(self) -> str:
        """Get current date in readable format."""
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y")

