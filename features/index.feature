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

  Scenario: Index suggests directive-based issue slug
    Given the issues directory contains an open issue "index-directive-suggestion"
    And the Git repository contains a commit "Fixes #index-directive-suggestion"
    When I visit the commit index
    Then the index row for the commit should show an issue suggestion "index-directive-suggestion"
    And the issue field for that commit should be blank

  Scenario: Index suggests touched issue slug when no directive
    Given the issues directory contains an open issue "index-touched-suggestion"
    And the Git repository contains a commit touching issue "index-touched-suggestion" with message "Update issue doc without directive"
    When I visit the commit index
    Then the index row for the commit should show an issue suggestion "index-touched-suggestion"

  Scenario: Index suggests issue slug mentioned in commit message
    Given the issues directory contains an open issue "index-message-suggestion"
    And the Git repository contains a commit "open index-message-suggestion"
    When I visit the commit index
    Then the index row for the commit should show an issue suggestion "index-message-suggestion"

  Scenario: Index does not suggest non-existent issue slug
    Given the Git repository contains a commit "Fixes #index-nonexistent"
    When I visit the commit index
    Then the index row for the commit should not show an issue suggestion

  @with_xlsx
  Scenario: Index rows have anchor IDs for back link targeting
    Given the server is running
    When I GET the root page
    Then the response should contain an anchor id for commit "middle"
