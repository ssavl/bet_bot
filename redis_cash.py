from redis import Redis
import requests
from bs4 import BeautifulSoup as bs
from config import user_agent, URL_24H
from pprint import pprint
import json
from datetime import datetime

r = Redis(host='localhost', port=6379, db=0)

data_test = {
    "name": "Ю.Киммельманн - В.Оляновская",
    "odds": {
      "20.03.2020:15:12": {
        "П1": "2.04",
        "П2": "1.78"
      },
      "20.03.2020:14:12": {
        "П1": "2.04",
        "П2": "1.78"
    }
  }
}

"""r.set("10860986", json.dumps(data))
"""


request = requests.get(URL_24H, headers=user_agent).text
soup = bs(request, 'html.parser')
coupons = soup.find('div', {'class': 'sport-category-content'}).find_all('div', {'class': 'bg coupon-row'})
tree_id = soup.find('div', {'class': 'sport-category-content'}).find_all('div', {'class': 'bg coupon-row'})[0]['data-event-treeid']  # вместо индекса просто будет итерация
name_members = soup.find('div', {'class': 'sport-category-content'}).find_all('div', {'class': 'bg coupon-row'})[0]['data-event-name']  # вместо индекса просто будет итерация
odd_p_1 = json.loads(coupons[0].find_all('td', {'class': 'price height-column-with-price first-in-main-row coupone-width-1'})[0]['data-sel'])['epr']  # отсюда можно вытащить все коэфициенты
odd_p_2 = json.loads(coupons[0].find_all('td', {'class': 'price height-column-with-price coupone-width-1'})[0]['data-sel'])['epr']  # отсюда можно вытащить все коэфициенты

step = 0

for coupon in coupons:

    id_ = coupon['data-event-treeid']
    members = coupon['data-event-name']
    time = str(datetime.now()).replace(" ", "")
    p1 = json.loads(coupon.find('td', {'class': 'price height-column-with-price first-in-main-row coupone-width-1'})['data-sel'])['epr']
    p2 = json.loads(coupon.find('td', {'class': 'price height-column-with-price coupone-width-1'})['data-sel'])['epr']

    data = {
        "name": members,
        "odds": {
            time: {
                "p1": round(float(p1), 2),
                "p2": round(float(p2), 2)
            }
        }
    }

    r.set(id_, json.dumps(data))

    # print('-' * 80)
    # print('ID матча:')
    # print(json.loads(coupon['data-event-treeid']))
    # print('Имя игроков:')
    # print(coupon['data-event-name'])
    # print('Текущее время:')
    # print(datetime.now())
    # print('Коэффициент П1')
    # print(json.loads(coupon.find('td', {'class': 'price height-column-with-price first-in-main-row coupone-width-1'})['data-sel'])['epr'])
    # print('Коэффициент П2')
    # print(json.loads(coupon.find('td', {'class': 'price height-column-with-price coupone-width-1'})['data-sel'])['epr'])


# step = 0
# for _ in result:
#     print('-' * 80)
#     print(_)
#     step = step + 1
#
# print(step)

































# r.mset({'Norway': 'Osli', 'Turkey': 'Istambul', 'Russia': 'Moscow'})  # Он принимает тут mapping, скорми ему словарики

# # ----------------------------Пример записи словаря в редис-----------------------------------------------------
# restaurant_484272 = {
#     "name": "Ravagh",
#     "type": "Persian",
#     "address": {
#         "street": {
#             "line1": "11 E 30th St",
#             "line2": "APT 1",
#         },
#         "city": "New York",
#         "state": "NY",
#         "zip": 10016,
#     }
# }
"""
r.set(484272, json.dumps(restaurant_484272))     <------------  Записываем вот таким образом

r.get(484272)    <--------------   Получаем таким образом

print(json.loads(r.get(484272)))  <--------------   Получаем нормальным образом
"""
# ----------------------------Пример записи словаря в редис-----------------------------------------------------


# pprint(json.loads(r.get(484272)))








# r.hmset(json.dumps({
#   "10860986": {
#     "name": "Ю.Киммельманн - В.Оляновская",
#     "odds": {
#       "20.03.2020:14:12": {
#         "П1": "2.04",
#         "П2": "1.78"
#       },
#       "20.03.2020:15:12": {
#         "П1": "2.04",
#         "П2": "1.78"
#       }
#     }
#   }
# }
# )
# )





# {"10860986":
# {"name": "Ю.Киммельманн - В.Оляновская",
# "odds":
# {"20.03.2020:14:12": {"П1": "2.04","П2": "1.78"}},
# {"20.03.2020:15:12": {"П1": "2.51","П2": "1.23"}}}