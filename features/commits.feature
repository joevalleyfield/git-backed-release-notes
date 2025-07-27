Feature: Commit Detail Page

  @with_xlsx
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

  Scenario: Commit detail back link targets index anchor
    Given a known commit "middle"
    When I GET the detail page for that commit
    Then the page should have a back link to the index anchor for that commit

  Scenario: Commit detail page links to parents and children
    Given a known commit "middle"
    When I GET the detail page for that commit
    Then the response should contain "Parents:"
    And the response should contain "Children:"
    And the page should contain a link to the parent of that commit
  
