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

  Scenario: Issue slug is shown and linked on the commit index
    Given a known commit "example" with issue "foo-bar"
    When I visit the commit index
    Then I should see a link to "/issue/foo-bar"

  @with_xlsx
  Scenario: Index rows have anchor IDs for back link targeting
    Given the server is running
    When I GET the root page
    Then the response should contain an anchor id for commit "middle"
