import pytest

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
except ImportError:
    pytest.skip("Selenium not installed; skipping UI tests",
                allow_module_level=True)


@pytest.fixture(scope="module")
def browser():
    opts = Options()
    opts.add_argument("--headless")
    driver = webdriver.Chrome(options=opts)
    yield driver
    driver.quit()


def test_subscription_form_submit(browser, live_server):
    url = f"{live_server.url}/subscribe"
    browser.get(url)

    browser.find_element(By.NAME, "email").send_keys("test@ui.com")
    browser.find_element(By.NAME, "city").send_keys("Amsterdam")
    browser.find_element(By.NAME, "temperature").send_keys("20")
    browser.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

    success = browser.find_element(By.CLASS_NAME, "alert-success").text
    assert "Subscription successful" in success
