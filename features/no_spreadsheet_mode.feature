@requires_dogfood_fixture
Feature: Run without spreadsheet input

  As a user with an existing Git repository
  I want to browse commits and issues
  Without supplying a spreadsheet
  So that I can use the app in "dogfooding" mode

  Scenario: Launching the app with no arguments on a repo containing issues/
    Given I am in a Git repository with an issues/ directory
    When I run "python app.py" with no arguments
    Then the index page should list recent commits
    And it should include a link to each commit detail page