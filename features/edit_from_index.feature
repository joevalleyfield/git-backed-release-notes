Feature: Edit commit metadata from index

  @with_xlsx
  Scenario: User edits the issue slug from the index page
    Given a known commit "middle"
    When I submit a new issue slug "edited-on-index" for that commit via the index form
    Then the response should contain the updated issue slug "edited-on-index"
    And the spreadsheet should contain the issue slug "edited-on-index" for that commit

  @with_xlsx
  Scenario: User edits the release field from the index page
    Given a known commit "initial"
    When I submit a new release value "rel-0.4" for that commit via the index form
    Then the response should contain the updated release value "rel-0.4"
    And the spreadsheet should contain the release value "rel-0.4" for that commit

  Scenario: Index page shows metadata form elements for each commit
    Given the server is running
    When I GET the root page
    Then the response should contain a form field "issue" for commit "middle"
    And the response should contain a form field "release" for commit "middle"