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