
Feature: Edit commit metadata

  @with_xlsx
  Scenario: User edits the issue slug for a commit
    Given a known commit "initial"
    When I submit a new issue slug "edit-issue-field-on-commit-page" for that commit
    Then the commit page should show the updated issue slug "edit-issue-field-on-commit-page"
    And the spreadsheet should contain the issue slug "edit-issue-field-on-commit-page" for that commit

  @with_xlsx
  Scenario: User edits the release field for a commit
    Given a known commit "middle"
    When I submit a new release value "rel-0.3" for that commit
    Then the commit page should show the updated release value "rel-0.3"
    And the spreadsheet should contain the release value "rel-0.3" for that commit

  @with_xlsx
  Scenario: Updating a commit that is not in the spreadsheet fails
    Given a known commit "latest"
    When I submit a new issue slug "ghost" for that commit
    Then the response status should be 404

  Scenario: Commit detail page shows metadata form without spreadsheet
    Given a known commit "middle"
    When I GET the detail page for that commit
    Then the page should contain a metadata form with an issue field
    And the page should contain a metadata form with a release field

  Scenario: User edits the release field for a commit with no spreadsheet
    Given a known commit "middle"
    When I submit a new release value "rel-0.3" for that commit
    Then the commit page should show the updated release value "rel-0.3"

