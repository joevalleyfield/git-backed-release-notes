Feature: Suggest primary issue on commit detail

  Scenario: Prefill issue field from directive when metadata is empty
    Given the issues directory contains an open issue "auto-suggest"
    Given the Git repository contains a commit "Fixes #auto-suggest"

    When the user visits the commit detail page for "Fixes #auto-suggest"
    Then the issue field should be prefilled with "auto-suggest"
    And the issue suggestion helper should mention "auto-suggest"

  Scenario: Preserve existing issue while offering a suggestion
    Given the issues directory contains an open issue "fresh-suggestion"
    Given the Git repository contains a commit "Fixes #fresh-suggestion"
    And the commit is linked to issue "already-linked"

    When the user visits the commit detail page for "Fixes #fresh-suggestion"
    Then the issue field should be prefilled with "already-linked"
    And I should see an issue suggestion button for "fresh-suggestion"

  Scenario: Do not suggest slugs without matching issues
    Given the Git repository contains a commit "Fixes #missing-issue"

    When the user visits the commit detail page for "Fixes #missing-issue"
    Then the issue field should be blank
    And no issue suggestion helper should be shown
