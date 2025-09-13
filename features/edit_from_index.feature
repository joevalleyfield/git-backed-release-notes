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

  @javascript
  Scenario: User edits the issue field and clicks away
    Given a known commit "middle"
    When the user edits the issue field to "foo-bar" and clicks away
    And the focus should be on the expected element after the save
    When I reload the page
    Then the issue value should be "foo-bar"

  @javascript
  Scenario: User edits the release field and clicks away
    Given a known commit "middle"
    When the user edits the release field to "rel-5.3" and clicks away
    And the focus should be on the expected element after the save
    When I reload the page
    Then the release value should be "rel-5.3"

  @javascript
  Scenario: User edits the release field and tabs away
    Given a known commit "middle"
    When the user edits the release field to "rel-5.4" and tabs away
    And the focus should be on the expected element after the save
    When I reload the page
    Then the release value should be "rel-5.4"

  Scenario: AJAX-style update returns 204 without redirect
    Given a known commit "middle"
    When I POST an AJAX metadata update for field "issue" with value "from-non-js"
    Then the response status should be 204
