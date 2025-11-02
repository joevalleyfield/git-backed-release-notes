Feature: Issue-centric browsing index

  Background:
    Given the server is running
    And the issues directory contains issue metadata for:
      | slug                           | status | release   | last_updated   |
      | open-ux-tweaks                | open   | release-a | 2024-02-14     |
      | closed-fix-off-by-one         | closed | release-a | 2024-02-11     |
      | closed-add-breadcrumbs        | closed | release-b | 2024-01-29     |
      | open-add-merge-guard          | open   | release-b | 2024-01-26     |
    And commit landing data exists for issues:
      | slug                    | landed_at         |
      | open-ux-tweaks          | 2024-02-13 10:00 |
      | closed-fix-off-by-one   | 2024-02-10 08:15 |
      | closed-add-breadcrumbs  | 2024-01-31 16:45 |
      | open-add-merge-guard    | 2024-02-01 09:30 |

  Scenario: Chronological view favors most recently updated issues
    When the user visits the issue index
    And selects the "Updated" sort
    Then the issue list should order slugs as:
      | position | slug                   |
      | 1        | open-ux-tweaks         |
      | 2        | closed-fix-off-by-one  |
      | 3        | closed-add-breadcrumbs |
      | 4        | open-add-merge-guard   |

  Scenario: Landing history view mirrors commit chronology
    When the user visits the issue index
    And selects the "Landed" sort
    Then the issue list should order slugs as:
      | position | slug                   |
      | 1        | open-ux-tweaks         |
      | 2        | closed-fix-off-by-one  |
      | 3        | open-add-merge-guard   |
      | 4        | closed-add-breadcrumbs |

  Scenario: Release filter surfaces cohort-specific issues
    When the user visits the issue index
    And filters issues by release "release-a"
    Then the issue list should show slugs:
      | slug                  | status |
      | open-ux-tweaks        | open   |
      | closed-fix-off-by-one | closed |

  Scenario: Issue index provides global commit navigation
    When the user visits the issue index
    Then the header should link to the commit index
    And the header should link to the release index
    And issue rows should not include commit navigation links

  Scenario: Last Landed derives from inferred commits
    Given landing data is cleared for issue "closed-add-breadcrumbs"
    And metadata links are cleared for issue "closed-add-breadcrumbs"
    And a commit touching issue "closed-add-breadcrumbs" landed at "2024-03-05T15:45:00+00:00"
    When the user visits the issue index
    Then issue "closed-add-breadcrumbs" should show last landed "2024-03-05 15:45"
