from datetime import datetime
import random
import time
from config import client_key, URL, bet_login, bet_password
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import WebDriverException, NoSuchElementException, ElementNotInteractableException, \
    InvalidSessionIdException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from pymongo import MongoClient
from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import re
import json


client = MongoClient(client_key)
db = client.testdb
firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument("--start-maximized")
set_of_events = set()
list_of_events = list(set_of_events)
driver = webdriver.Firefox()
TIME = str(datetime.now())


def START():
    try:
        print('-' * 30, 'НОВЫЙ МАТЧ', '-' * 30)
        driver.get(URL)
        driver.maximize_window()
        print('Ввожу учетные данные')
        driver.set_page_load_timeout(30)
        elem = driver.find_element_by_id('auth_login')  # бот авторизуется на сайте за сессию
        elem.clear()
        elem.send_keys(bet_login)
        elem = driver.find_element_by_id('auth_login_password')
        elem.clear()
        elem.send_keys(bet_password)
        elem.send_keys(Keys.RETURN)
        time.sleep(9)
    except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException,
            InvalidSessionIdException, WebDriverException):
        print('У нас возникла ошибка из семейства WebDriverException в START, пропускаю этот Match_Id')
        raise ValueError


def GET_LIST_EVENTS():  # НЕОБЯЗАТЕЛЬНАЯ ФУНКЦИЯ
    try:
        get_url_master = driver.current_url  # Получаю url страницы где список всех текущих событий в LIVE
        url = requests.get(get_url_master).text
        soup = bs(url, 'html.parser')
        for i in soup.select('td.category-label-td'):
            tree_id_event1 = re.findall(r'\d{7,8}', str(i))[0]
            set_of_events.add(tree_id_event1)
    except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException,
            InvalidSessionIdException, WebDriverException, IndexError):
        print('WebDriverException: в GET_LIST_EVENTS,возможно сейчас матчей в лайве НЕТ, пропускаю Match_Id'),
        raise ValueError


def GET_MATCH(num):
    list_for_FAST_get_match = []
    print(f'Текущие матчи = {list(set_of_events)}')
    try:
        id_match_now = list(set_of_events)[num]
    except IndexError:
        print('Мы дошли до конца, больше матчей НЕТ!'),
        raise ArithmeticError
    list_for_FAST_get_match.append(id_match_now)
    print(f'Работаю с матчем = {list_for_FAST_get_match[0]}')
    try:
        elem = driver.find_element_by_css_selector(
            f'#category{list_for_FAST_get_match[0]} > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > table:nth-child(1) > '
            f'tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > '
            f'tr:nth-child(2) > td:nth-child(2) > div:nth-child(1) > div:nth-child(3) > a:nth-child(1)')
        elem.click()
    except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException,
            InvalidSessionIdException, WebDriverException):
        print('У нас возникла ошибка из семейства WebDriverException в GET_MATCH, пропускаю этот Match_Id'),
        raise ValueError

# -----------------------------------------------------------------------------------------------------------


def get_event_id():  # tree_id == get_event_id, могу получить этот элемент из url или из html элементов
    try:
        get_url = driver.current_url
        tree_id = int(re.findall(r'\d{8}', get_url)[0])  # Регулярное выражение достающее 8-значное число из url
        return tree_id
    except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException,
            InvalidSessionIdException, WebDriverException, IndexError):
        print('У нас возникла ошибка из семейства WebDriverException в get_event_id, пропускаю этот Match_Id')
    raise ValueError


def get_data_selection_key():
    try:
        get_url = driver.current_url
        url_master = requests.get(get_url).text
        page_soup = bs(url_master, 'html.parser')
        element = page_soup.select('span.selection-link.active-selection')[4]['data-selection-key'][
              0:7]  # изменил элем. [4]
        return element
    except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException,
            InvalidSessionIdException, WebDriverException, IndexError):
        print('У нас возникла ошибка из семейства WebDriverException в get_data_selection_key, пропускаю этот Match_Id')
    raise ValueError


def get_odd_total():  # ПОЛУЧАЮ КОЭФ ТОТАЛ 2.5 МЕНЬШЕ (Важно! Может вернуть None!)
    try:
        list_of_id = []
        data_selection_key = get_data_selection_key()
        list_of_id.append(data_selection_key)
        get_url = driver.current_url
        url = requests.get(get_url).text
        soup = bs(url, 'html.parser')
        results = soup.select('span.selection-link.active-selection')
        for i in results:
            a = i['data-selection-key']
            if a == (f'{list_of_id[-1]}@Total_Sets.Under_2.5'):
                odd_span = i['data-selection-price']
                return float(odd_span)
    except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException, InvalidSessionIdException, WebDriverException, IndexError):
        print('У нас возникла ошибка из семейства WebDriverException в get_odd_total, пропускаю этот Match_Id')
        raise ValueError
# -----------------------------------------------------------------------------------------------------------



def TOTAL_CLICK():
    driver.set_page_load_timeout(30)
    list_for_FAST_get_match = []
    list_for_FAST_get_match.append(get_event_id())
    id_event = list_for_FAST_get_match[0]
    print(f'id_event = {id_event}')
    url = driver.current_url
    result = requests.get(url).text
    soup = bs(result, 'html.parser')
    index = soup.select('div.cl-left.red')
    print(f'тег индекс ==  {index}')
    if 'italic' in str(index):
        raise ValueError
    else:
        print('Сейчас идет первый сэт')
        try:
            elem = driver.find_element_by_css_selector(f'#shortcutLink_event{id_event}type10').click()
        except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException,
                InvalidSessionIdException, WebDriverException, IndexError):
            raise ValueError


def CYCLE_MASTER():
    driver.set_page_load_timeout(10)
    start_time = time.time()
    i = get_odd_total()
    cycle = True
    if i >= 2:
        print("Рабочий Кф больше 4, выходим из цикла")
        cycle = False
        raise TypeError
    else:
        try:
            while cycle:  # Вхожу в цикл, проверяю нужный мне коэффициент условием и либо делаю ставку, либо проверяю дальше
                time.sleep(12)
                t = get_odd_total()
                list_atr = []
                list_atr.append(get_event_id())
                print(f'Сейчас рабочий коэффициент = {t}')
                print('-' * 80)
                if time.time() - start_time > 300.01:
                    elem123 = driver.find_element_by_css_selector(
                    f'#block{list_atr[0]}type3 > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > div:nth-child(1) > div:nth-child(2)').click()
                    time.sleep(3)
                    elem9 = driver.find_element_by_css_selector('#header_bet_slip').click()
                    time.sleep(2)
                    elem1 = driver.find_element_by_xpath(
                    f'//*[@id="stake.{get_data_selection_key()},Total_Sets.Under_2.5"]')
                #WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="stake.{get_data_selection_key()},Total_Sets.Under_2.5"]')))
                    elem1.clear()
                    data = {TIME:str(t)}
                    time.sleep(3)
                    elem1.send_keys(20)
                    time.sleep(3)
                    elem1.send_keys(20)
                    time.sleep(3)
                    driver.find_element_by_xpath('//*[@id="betslip_placebet_btn_id"]').click()
                    time.sleep(19)
                    if "Пари принято" in driver.page_source:
                        elem = driver.find_element_by_css_selector('#ok-button').click(), print(
                        "Пари принято"), driver.close(), db.testcollection.insert_one({str(datetime.now()):str(t)})
                    elif 'Извините, Ваша ставка в пари не принята.' in driver.page_source:
                        elem = driver.find_element_by_css_selector('#place-changed-terms').click(), print(
                        "Ставка не прошла"), driver.close(), db.testcollection.insert_one({str(datetime.now()):str('error')})
                    else:
                        print('Возникли какие-то проблемы при проставлении ставки'), db.testcollection.insert_one({str(datetime.now()):str('error')})
                    cycle = False
                if t >= 1.6:
                    driver.set_page_load_timeout(30)
                    print(f'Сейчас кф = {t}, делаю ставку!')
                    elem123 = driver.find_element_by_css_selector(
                    f'#block{list_atr[0]}type3 > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > div:nth-child(1) > div:nth-child(2)').click()
                    elem9 = driver.find_element_by_css_selector('#header_bet_slip').click()
                    time.sleep(3)
                    elem1 = driver.find_element_by_xpath(
                    f'//*[@id="stake.{get_data_selection_key()},Total_Sets.Under_2.5"]')
                #WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="stake.{get_data_selection_key()},Total_Sets.Under_2.5"]')))
                    elem1.clear()
                    data = {str(datetime.now()):str(t)}
                    time.sleep(3)
                    elem1.send_keys(20)
                    time.sleep(3)
                    driver.find_element_by_xpath('//*[@id="betslip_placebet_btn_id"]').click()
                    time.sleep(19)
                    if "Пари принято" in driver.page_source:
                        elem = driver.find_element_by_css_selector('#ok-button').click(), print(
                                "Пари принято"), driver.close(), db.testcollection.insert_one({str(datetime.now()):str(t)})
                    elif 'Извините, Ваша ставка в пари не принята.' in driver.page_source:
                        elem = driver.find_element_by_css_selector('#place-changed-terms').click(), print("Ставка не прошла"), driver.close(), db.testcollection.insert_one({str(datetime.now()):str('Ставка не прошла')})
                    else:
                        print('Возникли какие-то проблемы при проставлении ставки'), db.testcollection.insert_one({str(datetime.now()):str('error')})
                    cycle = False
                else:
                    print(f'Рабочий коэффициент должен быть = от 1.6 или выше, сейчас он {t}'),\
                    print(f'Цикл выполняется уже {time.time() - start_time} секунд') ,print('-' * 80)

        except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException,
                 InvalidSessionIdException, WebDriverException, IndexError, TypeError):
            print('У нас возникла ошибка из семейства WebDriverException в CYCLE_MASTER, пропускаю этот Match_Id'), db.testcollection.insert_one({str(datetime.now()):str('Ставка не прошла')})
            raise ValueError



def final_func(num):
    try:
        START()
        GET_LIST_EVENTS()
        time.sleep(10)
        GET_MATCH(num)
        time.sleep(10)
        TOTAL_CLICK()
        time.sleep(10)
        CYCLE_MASTER()
    except TypeError:
        driver.close()
        print('Type Error')
        pass
    except ValueError:
        driver.close()
        print('Value Error')
        pass
    except ArithmeticError:
        driver.close()
        print('Arithmetic Error')
        quit()


final_func(0)
# driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', options=firefox_options)
driver = webdriver.Firefox()
final_func(1)
# driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', options=firefox_options)
driver = webdriver.Firefox()
final_func(2)
# driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', options=firefox_options)
driver = webdriver.Firefox()
final_func(3)
# driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', options=firefox_options)
driver = webdriver.Firefox()
final_func(4)
# driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', options=firefox_options)
driver = webdriver.Firefox()
final_func(5)
# driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', options=firefox_options)
driver = webdriver.Firefox()
final_func(6)
# driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', options=firefox_options)
driver = webdriver.Firefox()
final_func(7)
# driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', options=firefox_options)
driver = webdriver.Firefox()
final_func(8)
# driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', options=firefox_options)
driver = webdriver.Firefox()
final_func(9)
# driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', options=firefox_options)
driver = webdriver.Firefox()
final_func(10)
# driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', options=firefox_options)
