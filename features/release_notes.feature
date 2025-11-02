Feature: Release notes browsing

  Background:
    Given the server is running
    And release issues exist:
      | slug            | status | release   |
      | closed-bugfix   | closed | release-a |
      | closed-feature  | closed | release-b |
    And release metadata assigns commits to releases:
      | commit_label | issue          | release   |
      | initial      | closed-bugfix  | release-a |
      | middle       | closed-feature | release-b |

  Scenario: Release index and detail aggregate commits and issues
    When the user visits the release index
    Then the release list should show:
      | release   | issue_count | commit_count |
      | release-a | 1           | 1            |
      | release-b | 1           | 1            |
    When the user visits the release detail for "release-a"
    Then the release detail should list issues:
      | issue_slug    | status |
      | closed-bugfix | closed |
    And the release detail should list commits:
      | commit_label |
      | initial      |
    And the release detail should include issue note heading "Closed Bugfix"
    And the release detail should show summary "1 issue • 1 commit"
    And release issues should link to their detail pages
    And release commits should link to their detail pages
    And the release detail should surface tag metadata
