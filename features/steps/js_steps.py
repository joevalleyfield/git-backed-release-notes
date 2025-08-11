from behave import when, then
from playwright.sync_api import expect
import time

def _input_for_current_sha(page, sha, name):
    # Inputs are not inside <form>; they reference it via [form="form-<sha>"]
    return page.locator(f'input[name="{name}"][form="form-{sha}"]')

@when('the user edits the issue field to "{value}" and clicks away')
def step_edit_issue_blur(context, value):
    base_url = getattr(context, "base_url", "http://localhost:8888")
    sha = context.commit_sha

    context.page.goto(f"{base_url}/", wait_until="domcontentloaded")

    # Ensure form and input exist
    form_sel = f'form#form-{sha}'
    input_sel = f'input[name="issue"][form="form-{sha}"]'
    context.page.wait_for_selector(form_sel, state="attached", timeout=3000)
    context.page.wait_for_selector(input_sel, state="visible", timeout=3000)

    issue = _input_for_current_sha(context.page, sha, "issue")
    expect(issue).to_be_visible(timeout=3000)

    try:
        # Wait for the POST to complete
        with context.page.expect_response(
            lambda r: r.url.endswith(f"/commit/{context.commit_sha}/update") and r.request.method == "POST",
            timeout=3000
        ):
            issue.fill(value)
            context.page.locator("header h1").click()

        context.page.wait_for_load_state("networkidle", timeout=3000)
    except Exception:
        ts = int(time.time())
        context.page.screenshot(path=f"playwright_fail_{ts}.png", full_page=True)
        html = context.page.content()
        with open(f"playwright_fail_{ts}.html", "w", encoding="utf-8") as f:
            f.write(html)
        raise

@then('the issue value should be "{value}"')
def step_assert_issue_value(context, value):
    base_url = getattr(context, "base_url", "http://localhost:8888")
    sha = context.commit_sha

    context.page.goto(f"{base_url}/", wait_until="domcontentloaded")

    input_sel = f'input[name="issue"][form="form-{sha}"]'
    context.page.wait_for_selector(input_sel, state="visible", timeout=3000)
    issue = _input_for_current_sha(context.page, sha, "issue")
    expect(issue).to_have_value(value, timeout=3000)

@when('the user edits the release field to "{value}" and clicks away')
def step_edit_release_blur(context, value):
    base_url = getattr(context, "base_url", "http://localhost:8888")
    sha = context.commit_sha

    context.page.goto(f"{base_url}/", wait_until="domcontentloaded")
    form_sel = f'form#form-{sha}'
    input_sel = f'input[name="release"][form="form-{sha}"]'
    context.page.wait_for_selector(form_sel, state="attached", timeout=3000)
    context.page.wait_for_selector(input_sel, state="visible", timeout=3000)

    release = _input_for_current_sha(context.page, sha, "release")
    expect(release).to_be_visible(timeout=3000)

    with context.page.expect_response(
        lambda r: r.url.endswith(f"/commit/{sha}/update") and r.request.method == "POST",
        timeout=3000
    ):
        release.fill(value)
        context.page.locator("header h1").click()

    context.page.wait_for_load_state("networkidle", timeout=3000)

@then('the release value should be "{value}"')
def step_assert_release_value(context, value):
    base_url = getattr(context, "base_url", "http://localhost:8888")
    sha = context.commit_sha

    context.page.goto(f"{base_url}/", wait_until="domcontentloaded")
    release = _input_for_current_sha(context.page, sha, "release")
    expect(release).to_have_value(value, timeout=3000)
