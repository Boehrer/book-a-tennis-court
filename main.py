"""
This module contains a script which uses selenium to automatically book
tennis courts.
"""
from time import sleep
from datetime import datetime, timedelta

import os

import pytz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

from secrets import (
    EMAIL_ADDRESS,
    PASSWORD,
    CARD_HOLDER,
    CARD_NUMBER,
    CVC,
    EXPIRATION_MONTH,
    EXPIRATION_YEAR,
    EVENT_NAME,
    URL,
)


ROWS_XPATH = '//*[@role="grid"]//*[@role="row"]'
SIGN_IN_PAGE_XPATH = '//a[@class="reservation-quick__signin-now-link"]'
SIGN_IN_BUTTON_XPATH = '//div[@class="signin__action"]/button'
EMAIL_INPUT_XPATH = '//input[@aria-label="Email address Required"]'
PASSWORD_INPUT_XPATH = '//input[@aria-label="Password Required"]'
CALENDAR_INPUT_XPATH = '//input[@aria-label="Date picker, current date"]'
NEXT_MONTH_BUTTON_XPATH = '//i[@aria-label="Switch calendar to next month right arrow"]'
DATE_XPATH_TEMPLATE = '//tr[@class="an-calendar-table-row"]//div[text()="{day_of_month}"]'
EVENT_NAME_INPUT_XPATH = '//input[@data-qa-id="quick-reservation-eventType-name"]'
CONFIRM_BUTTON_XPATH = '//button[@data-qa-id="quick-reservation-ok-button"]'
RESERVE_BUTTON_XPATH = '//button[@data-qa-id="quick-reservation-reserve-button"]'
PAYMENT_IFRAME_XPATH = '//div[@class="module-checkout"]//iframe'
CARD_HOLDER_INPUT_XPATH = '//input[@name="holderName"]'
CARD_NUMBER_INPUT_XPATH = '//input[@name="cardNumber"]'
EXPIRATION_MONTH_DROPDOWN_XPATH = '//select[@class="dropdown" and @name="month"]'
EXPIRATION_YEAR_DROPDOWN_XPATH = '//select[@class="dropdown" and @name="year"]'
CVC_INPUT_XPATH = '//input[@name="cvv"]'
BILLING_ADDRESS_DROPDOWN_XPATH = '//div[@class="dropdown__button input__field"]/span[@class="dropdown__button-text"]'
BILLING_ADDRESS_OPTION_XPATH = '//div[@class="option-content__text" and text()="Jack Boehrer"]'
PAY_BUTTON_XPATH = '//button[@data-qa-id="checkout-orderSummary-payBtn"]'
VALID_HOUR_LOWER_BOUND = 6
VALID_HOUR_UPPER_BOUND = 22
TIMEOUT_SECONDS = 60
DAYS_IN_ADVANCE = 6
TENNIS_COURT = "Tennis Ct"
ACCEPTABLE_HOURS = [int(h) for h in os.environ.get("ACCEPTABLE_HOURS", "18,19,20").split(",")]


def get_driver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=chrome_options)


class Cell:
    def __init__(self, element: WebElement):
        self.element = element

    def is_available(self) -> bool:
        return "disabled" not in self.element.get_attribute("class")


class Row:
    def __init__(self, element: WebElement):
        self.element = element
        self.resource = element.find_element(
            By.XPATH,
            './/div[@class="resource-header-cell__name"]/span'
        ).text

    def get_cells(self) -> list[WebElement]:
        return [Cell(e) for e in self.element.find_elements(By.XPATH, './td')]


class Table:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def get_rows(self) -> list[Row]:
        return [
            Row(element)
            for element in self.driver.find_elements(By.XPATH, ROWS_XPATH)
        ]

    def find_available_courts(
        self,
        acceptable_hours: list[int],
    ) -> list[Cell]:
        rows = [
            row for row in self.get_rows() if TENNIS_COURT in row.resource
        ]
        available_courts = []
        for row in rows:
            cells = row.get_cells()
            for hour in acceptable_hours:
                cell_index = hour - 6
                cell = cells[cell_index]
                if cell.is_available():
                    available_courts.append(cell)
        return available_courts


if __name__ == "__main__":
    current_date = datetime.now(pytz.timezone("America/Chicago")).date()
    desired_date = current_date + timedelta(days=DAYS_IN_ADVANCE)
    driver = get_driver()
    driver.get(URL)
    # sign in
    sign_in_page = WebDriverWait(driver, TIMEOUT_SECONDS).until(
        EC.element_to_be_clickable((By.XPATH, SIGN_IN_PAGE_XPATH))
    )
    sign_in_page.click()
    email_input_element = WebDriverWait(driver, TIMEOUT_SECONDS).until(
        EC.presence_of_element_located((By.XPATH, EMAIL_INPUT_XPATH))
    )
    password_input_element = driver.find_element(
        By.XPATH, PASSWORD_INPUT_XPATH
    )
    email_input_element.send_keys(EMAIL_ADDRESS)
    password_input_element.send_keys(PASSWORD)
    sign_in_button = driver.find_element(By.XPATH, SIGN_IN_BUTTON_XPATH)
    now = datetime.now(pytz.timezone("America/Chicago"))
    target = now.replace(hour=7, minute=0, second=0, microsecond=0)
    if now < target:
        seconds = (target - now).total_seconds()
        print(f"sleeping for {seconds:.1f} seconds")
        sleep(seconds)
    sign_in_button.click()
    # select six days in advance
    calendar_input = WebDriverWait(driver, TIMEOUT_SECONDS).until(
        EC.element_to_be_clickable((By.XPATH, CALENDAR_INPUT_XPATH))
    )
    calendar_input.click()
    if desired_date.month != current_date.month:
        next_month_button = WebDriverWait(driver, TIMEOUT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, NEXT_MONTH_BUTTON_XPATH))
        )
        next_month_button.click()
    day_of_month_element = WebDriverWait(driver, TIMEOUT_SECONDS).until(
        EC.element_to_be_clickable((By.XPATH, DATE_XPATH_TEMPLATE.format(day_of_month=desired_date.day)))
    )
    day_of_month_element.click()
    # select available courts
    WebDriverWait(driver, TIMEOUT_SECONDS).until(
        EC.presence_of_element_located((By.XPATH, ROWS_XPATH))
    )
    available_courts = Table(driver).find_available_courts(ACCEPTABLE_HOURS)
    try:
        best_court = available_courts[0]
    except IndexError:
        raise RuntimeError("no acceptable court available")
    best_court.element.click()
    event_name_input_element = driver.find_element(
        By.XPATH, EVENT_NAME_INPUT_XPATH
    )
    event_name_input_element.send_keys(EVENT_NAME)
    confirm_button = WebDriverWait(driver, TIMEOUT_SECONDS).until(
        EC.element_to_be_clickable((By.XPATH, CONFIRM_BUTTON_XPATH))
    )
    confirm_button.click()
    reserve_button = WebDriverWait(driver, TIMEOUT_SECONDS).until(
        EC.element_to_be_clickable((By.XPATH, RESERVE_BUTTON_XPATH))
    )
    reserve_button.click()
    # pay for courts
    iframe_element = WebDriverWait(driver, TIMEOUT_SECONDS).until(
        EC.presence_of_element_located((By.XPATH, PAYMENT_IFRAME_XPATH))
    )
    driver.switch_to.frame(iframe_element)
    card_holder_input_element = WebDriverWait(driver, TIMEOUT_SECONDS).until(
        EC.presence_of_element_located((By.XPATH, CARD_HOLDER_INPUT_XPATH))
    )
    card_holder_input_element.send_keys(CARD_HOLDER)
    card_number_input_element = driver.find_element(
        By.XPATH, CARD_NUMBER_INPUT_XPATH
    )
    card_number_input_element.send_keys(CARD_NUMBER)
    cvc_input_element = driver.find_element(
        By.XPATH, CVC_INPUT_XPATH
    )
    cvc_input_element.send_keys(CVC)
    expiration_month_dropdown_element = driver.find_element(
        By.XPATH, EXPIRATION_MONTH_DROPDOWN_XPATH
    )
    expiration_month_dropdown = Select(expiration_month_dropdown_element)
    expiration_month_dropdown.select_by_visible_text(EXPIRATION_MONTH)
    expiration_year_dropdown_element = driver.find_element(
        By.XPATH, EXPIRATION_YEAR_DROPDOWN_XPATH
    )
    expiration_year_dropdown = Select(expiration_year_dropdown_element)
    expiration_year_dropdown.select_by_visible_text(EXPIRATION_YEAR)
    driver.switch_to.default_content()
    billing_address_dropdown_element = driver.find_element(
        By.XPATH, BILLING_ADDRESS_DROPDOWN_XPATH
    )
    billing_address_dropdown_element.click()
    billing_address_option = WebDriverWait(driver, TIMEOUT_SECONDS).until(
        EC.element_to_be_clickable((By.XPATH, BILLING_ADDRESS_OPTION_XPATH))
    )
    billing_address_option.click()
    pay_button = driver.find_element(
        By.XPATH, PAY_BUTTON_XPATH
    )
    pay_button.click()