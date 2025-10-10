from typing import Literal

from behave import then, when
from playwright.sync_api import expect


def _active_matches(page, selector: str) -> bool:
    return page.evaluate(
        """sel => {
      const a = document.activeElement;
      try { return a && a.matches(sel); } catch { return false; }
    }""",
        selector,
    )


def _active_debug(page):
    return page.evaluate(
        """() => {
      const a = document.activeElement;
      if (!a) return {html: null, desc: "null"};
      const desc = a.tagName.toLowerCase()
        + (a.id ? "#" + a.id : "")
        + (a.name ? `[name="${a.name}"]` : "")
        + (a.getAttribute && a.getAttribute("form") ? `[form="${a.getAttribute("form")}"]` : "");
      return {html: a.outerHTML, desc};
    }"""
    )


def _input_for_current_sha(page, sha, name):
    # Inputs are not inside <form>; they reference it via [form="form-<sha>"]
    return page.locator(f'input[name="{name}"][form="form-{sha}"]')


def _edit_field_and_leave(
    context,
    field: Literal["issue", "release"],
    value: str,
    mode: Literal["click", "tab"],
) -> None:
    """
    Shared implementation for editing a field and leaving focus either by clicking away or tabbing.
    Sets context.expected_focus_selector (CSS) for the later assertion step.
    """
    base_url = getattr(context, "base_url", "http://localhost:8888")
    sha = context.commit_sha

    context.page.goto(f"{base_url}/", wait_until="domcontentloaded")
    form_sel = f"form#form-{sha}"
    input_sel = f'input[name="{field}"][form="form-{sha}"]'
    context.page.wait_for_selector(form_sel, state="attached", timeout=3000)
    context.page.wait_for_selector(input_sel, state="visible", timeout=3000)

    current = _input_for_current_sha(context.page, sha, field)
    expect(current).to_be_visible(timeout=3000)

    # Focus and set the value (replace existing content).
    current.click()
    current.fill(value)
    expect(current).to_have_value(value, timeout=1000)

    if mode == "click":
        # Deterministic click-away: always switch to the sibling input in the same row.
        other = "release" if field == "issue" else "issue"
        next_sel = f'input[name="{other}"][form="form-{sha}"]'
        context.expected_focus_selector = next_sel
        target = context.page.locator(next_sel).first
        target.scroll_into_view_if_needed()
        target.click()
    else:
        # Tab to the *actual* next tabbable (could be an <a>)
        current.press("Tab")
        context.expected_focus_selector = _selector_for_active(context.page)

    # Give any AJAX/debounced save a beat to complete (tune or remove per your app).
    context.page.wait_for_load_state("networkidle", timeout=3000)


def _selector_for_active(page) -> str | None:
    # Returns stable CSS for activeElement (input[name][form] or a[href]), else tag name.
    return page.evaluate(
        """
        () => {
          const a = document.activeElement;
          if (!a) return null;
          if (a.tagName === 'INPUT' && a.name && a.getAttribute('form')) {
            return 'input[name="' + a.name + '"][form="' + a.getAttribute('form') + '"]';
          }
          if (a.tagName === 'A' && a.getAttribute('href')) {
            return 'a[href="' + a.getAttribute('href') + '"]';
          }
          return a.tagName.toLowerCase();
        }
    """
    )


@when("I reload the page")
def step_reload_page(context):
    # Stay on current route; ensures we validate server round-trip after AJAX save.
    context.page.reload(wait_until="domcontentloaded")
    context.page.wait_for_load_state("networkidle", timeout=3000)


@when('the user edits the {field} field to "{value}" and {navigation_mode} away')
def step_edit_field_leave(
    context,
    field: Literal["issue", "release"],
    value: str,
    navigation_mode: Literal["clicks", "tabs"],
):
    _edit_field_and_leave(context, field, value, mode=navigation_mode.rstrip("s"))


@then('the issue value should be "{value}"')
def step_assert_issue_value(context, value):
    sha = context.commit_sha
    issue = _input_for_current_sha(context.page, sha, "issue")
    expect(issue).to_have_value(value, timeout=3000)


@then('the release value should be "{value}"')
def step_assert_release_value(context, value):
    sha = context.commit_sha
    release = _input_for_current_sha(context.page, sha, "release")
    expect(release).to_have_value(value, timeout=3000)


@when("the focus should be on the expected element after the save")
def step_cursor_on_expected(context):
    assert getattr(context, "expected_focus_selector", None), "expected_focus_selector was not set"
    ok = _active_matches(context.page, context.expected_focus_selector)
    if not ok:
        dbg = _active_debug(context.page)
        raise AssertionError(
            f"Focus was not on: {context.expected_focus_selector!r}\n"
            f"Active element: {dbg['desc']}\n"
            f"OuterHTML: {dbg['html']}"
        )
