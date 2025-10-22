Feature: Suggest primary issue on commit detail

  Scenario: Prefill issue field from directive when metadata is empty
    Given the issues directory contains an open issue "auto-suggest"
    Given the Git repository contains a commit "Fixes #auto-suggest"

    When the user visits the commit detail page for "Fixes #auto-suggest"
    Then the issue field should be prefilled with "auto-suggest"
    And the issue suggestion helper should link to "auto-suggest"

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

  Scenario: Suggest issue from touched file when no directive
    Given the issues directory contains an open issue "touched-suggestion"
    And the Git repository contains a commit touching issue "touched-suggestion" with message "Update issue doc without directive"

    When the user visits the commit detail page for "Update issue doc without directive"
    Then the issue field should be prefilled with "touched-suggestion"
    And the issue suggestion helper should link to "touched-suggestion"

  Scenario: Suggest issue from message slug without directive
    Given the issues directory contains an open issue "message-suggestion"
    And the Git repository contains a commit "open message-suggestion"

    When the user visits the commit detail page for "open message-suggestion"
    Then the issue field should be prefilled with "message-suggestion"
    And the issue suggestion helper should link to "message-suggestion"
