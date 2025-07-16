Feature: View commit index

  @with_xlsx
  Scenario: User loads the main commit index
    Given the server is running
    When I GET the root page
    Then the response should contain "Commit"

  Scenario: Index shows all commits when no spreadsheet is provided
    Given the server is running without a spreadsheet
    When I GET the root page
    Then the response should contain "Commit"

  @with_xlsx
  Scenario: Issue slug is shown in the index table
    Given the server is running
    When I GET the root page
    Then the response should contain the issue slug "display-issue-slugs-in-index"
