Feature: Edit issues and link commits without a spreadsheet

  Background:
    Given the server is running without a spreadsheet
    And the issues directory contains an open issue "foo-bar"
    And the Git repository contains a commit "Add behavior for foo-bar"

  Scenario: User edits an issue Markdown field
    When the user visits the issue "foo-bar" detail page
    And the user changes the "status" field to "in-progress"
    And the user saves the issue
    Then the issue file "foo-bar.md" should contain "status: in-progress"

  Scenario: User links a commit to an issue
    When the user visits the commit detail page for "Add behavior for foo-bar"
    And the user links the commit to issue "foo-bar"
    Then the issue "foo-bar" should show the commit "Add behavior for foo-bar"
    And a metadata file should record the link between the commit and issue
