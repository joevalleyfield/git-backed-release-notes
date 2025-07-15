@with_xlsx
Feature: Commit Detail Page

  Scenario Outline: Commit detail shows correct follows and precedes
    Given a known commit "<commit_label>"
    When I GET the detail page for that commit
    Then the page should show follows "<follows_tag>"
    And the page should show precedes "<precedes_tag>"

    Examples:
      | commit_label | follows_tag | precedes_tag |
      | initial      | (none)      | rel-0.2      |
      | middle       | rel-0.1     | rel-0.2      |
      | latest       | (none)      | (none)       |
