from behave import given, when, then

# run with:
# poetry run behave tests/features

@given('we have behave installed')
def step_impl_given(context):
    pass


@when('we implement {number:d} tests')
def step_impl_when(context, number):
    assert number > 1 or number == 0
    context.tests_count = number


@then('behave will test them for us!')
def step_impl_then(context):
    assert context.failed is False
    assert context.tests_count >= 0
