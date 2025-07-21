
Feature: View issue metadata from Markdown files

  Background:
    Given the server is running in file-backed mode
    And the issues directory contains an open issue "foo-bar"
    And the Git repository contains a commit "Fix the thing"

  Scenario: Issue page renders the Markdown content
    When the user visits the issue "foo-bar" detail page
    Then the response should contain "status: open"

  Scenario: Issue page lists linked commits
    Given the commit is linked to issue "foo-bar"
    When the user visits the issue "foo-bar" detail page
    Then the issue "foo-bar" should show the commit "Fix the thing"
