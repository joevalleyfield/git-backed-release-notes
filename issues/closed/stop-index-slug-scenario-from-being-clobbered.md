# Stop index slug scenario from being clobbered

The Behave suite shares a single spreadsheet-backed fixture across scenarios. Edit flows were mutating the slug that the index scenario later asserts on because the edit step grabbed the commit via `sha_map["middle"]`, which happened to be seeded with the `display-issue-slugs-in-index` slug. The fix introduces a semantic `issue_map` in the fixture so steps can target the commit linked to `allow-editing`, leaving the display slug untouched. This keeps shared fixtures fast while preventing state bleed between scenarios.
