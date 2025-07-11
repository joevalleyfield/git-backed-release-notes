@requires_remediation_fixture
Feature: View commit index

  Scenario: User loads the main commit index
    Given the server is running
    When I GET the root page
    Then the response should contain "Commit"
