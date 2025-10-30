Feature: Suggest release from Precedes tag

  Scenario: Surface release suggestion when Precedes resolves to a known tag
    Given a known commit "middle"

    When I GET the detail page for that commit
    Then the release field should be blank
    And I should see a release suggestion button for "rel-0.2" from source "Precedes"

  Scenario: Surface release suggestion when commit carries the release tag
    Given a known commit "initial"

    When I GET the detail page for that commit
    Then the release field should be blank
    And I should see a release suggestion button for "rel-0.1" from source "Tag"
