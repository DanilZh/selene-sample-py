from common_imports import *
from selene.helpers import env

browser_instance = env('selene_browser_name') or config.Browser.CHROME
base_url = "https://github.com"


@pytest.fixture(scope="session", autouse=True)
def setup_browser():
    # setup browser
    config.browser_name = browser_instance
    config.maximize_window = True

    # turn off selene auto-screenshots
    from selene import helpers
    helpers.take_screenshot = lambda *x: "See attachments"
    yield None


@pytest.fixture(scope="session", autouse=True)
def allure_config():
    # setup allure environment
    allure.environment(report="Selene Sample .py", browser=browser_instance, hostname=base_url)


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    return rep


@pytest.fixture(scope="function")
def screenshot_on_failure(request):
    yield None
    attach = browser.driver().get_screenshot_as_png()
    if request.node.rep_setup.failed:
        allure.attach(request.function.__name__, attach, allure.attach_type.PNG)
    elif request.node.rep_setup.passed:
        if request.node.rep_call.failed:
            allure.attach(request.function.__name__, attach, allure.attach_type.PNG)


@pytest.fixture()
def reset_driver_state():
    browser.visit(base_url)

    yield None
    browser.driver().delete_all_cookies()
