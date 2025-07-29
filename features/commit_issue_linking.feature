Feature: Cross-link commits and issues

  Scenario: Commit message references an issue by slug
    Given the issues directory contains an open issue "add-slug-linking-in-commit-messages"
    And the Git repository contains a commit "Implements #add-slug-linking-in-commit-messages"

    When the user visits the commit detail page for "Implements #add-slug-linking-in-commit-messages"
    Then I should see a link to "/issue/add-slug-linking-in-commit-messages"

    When the user visits the issue "add-slug-linking-in-commit-messages" detail page
    Then the issue "add-slug-linking-in-commit-messages" should show the commit "Implements #add-slug-linking-in-commit-messages"

  Scenario: Commit touches an issue file but has no slug in the message
    Given an uncommitted issue file named "implicit-link-via-touched-issue.md" with contents:
      """
      # 🧩 Some Issue

      This issue was created to test implicit linking when a commit touches the file.
      """
    And the Git repository contains a commit "Create new issue file"

    When the user visits the commit detail page for "Create new issue file"
    Then I should see a link to "/issue/implicit-link-via-touched-issue"

    When the user visits the issue "implicit-link-via-touched-issue" detail page
    Then the issue "implicit-link-via-touched-issue" should show the commit "Create new issue file"