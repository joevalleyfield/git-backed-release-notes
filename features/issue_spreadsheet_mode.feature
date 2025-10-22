Feature: Issue view with spreadsheet metadata

  @with_xlsx
  Scenario: Issue page lists commits from spreadsheet-backed metadata
    Given the server is running
    And the issues directory contains an open issue "display-issue-slugs-in-index"
    And a known commit "middle" with issue "display-issue-slugs-in-index"
    When the user visits the issue "display-issue-slugs-in-index" detail page
    Then the issue "display-issue-slugs-in-index" should show the commit "Second commit (middle)"
