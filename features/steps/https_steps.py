import requests
from behave import when

@when('I POST an AJAX metadata update for field "{field}" with value "{value}"')
def step_post_ajax_update(context, field, value):
    base_url = getattr(context, "base_url", "http://localhost:8888")
    sha = context.commit_sha
    url = f"{base_url}/commit/{sha}/update"   # no ?next= for AJAX
    data = {field: value}
    headers = {"X-Requested-With": "fetch"}

    # Store in the same attribute your other steps expect
    context.response = requests.post(url, data=data, headers=headers)
