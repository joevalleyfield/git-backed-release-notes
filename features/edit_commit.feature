
Feature: Edit commit metadata

  @with_xlsx
  Scenario: User edits the issue slug for a commit
    Given a known commit "initial"
    When I submit a new issue slug "edit-issue-field-on-commit-page" for that commit
    Then the commit page should show the updated issue slug "edit-issue-field-on-commit-page"
    And the spreadsheet should contain the issue slug "edit-issue-field-on-commit-page" for that commit

  @with_xlsx
  Scenario: Updating a commit that is not in the spreadsheet fails
    Given a known commit "latest"
    When I submit a new issue slug "ghost" for that commit
    Then the response status should be 404

  Scenario: Editing a commit when no spreadsheet is loaded fails
    Given the server is running without a spreadsheet
    And a known commit "initial"
    When I submit a new issue slug "oops" for that commit
    Then the response status should be 500