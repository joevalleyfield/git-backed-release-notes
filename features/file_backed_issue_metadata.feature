Feature: File-backed issue interface

  Covers viewing and editing of issue content from Markdown files, and
  displaying associated commit metadata when no spreadsheet is configured.en no
  spreadsheet is configured.

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

  Scenario: User edits issue content in Markdown
    When the user visits the issue "foo-bar" detail page
    And the user updates the issue content to include "This affects the widget subsystem."
    And the user saves the issue
    Then the issue file "foo-bar.md" should contain "This affects the widget subsystem."

  Scenario: User edits a closed issue
    Given the issues directory contains a closed issue "frobnicator-issue"
    When the user visits the issue "frobnicator-issue" detail page
    And the user updates the issue content to include "This affects the frobnicator."
    And the user saves the issue
    Then the closed issue file "frobnicator-issue.md" should contain "This affects the frobnicator."
