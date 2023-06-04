import json
from bs4 import BeautifulSoup
# bot 인줄 알고 차단당해서 selenium 써야함
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib.parse import unquote
import csv
import re

ko_to_en = {
    "월세": "realEstate_monthly_payment",
    "보증금": "realEstate_deposit",
    "관리비": "managementFees",
    "방종류": "realEstate_space_type",
    "전용면적": "realEstate_room_size",
    "전용/공급면적": "realEstate_room_size",
    "방향": "realEstate_window_direction",
    "입주가능일": "realEstate_occupancy_periods",
    "건축물용도": "realEstate_building_type",
    "사용승인일": "realEstate_built_date",
    "지번주소": "realEstate_areaNumberAddress",
    "도로명주소": "realEstate_roadAddress",
    "싱크대": "sink_status",
    "에어컨": "aircondition_status",
    "신발장": "shoebox_status",
    "세탁기": "washingMachine_status",
    "냉장고": "refrigerator_status",
    "옷장": "closet_status",
    "가스레인지": "gasStoves_status",
    "침대": "bed_status",
    "상세 설명": "detail_info",
    "카페": "cafe_status",
    "편의점": "convenienceStore_status",
    "세탁소": "laundry_status",
    "대형마트": "supermarket_status",
    "버스정류장": "busStation_status",
    "지하철역": "subway_status"
}

real_estate = [
    'realEstate_roadAddress',
    'realEstate_areaNumberAddress',
    'jeonse_monthlyRent_type',
    'realEstate_deposit',
    'realEstate_monthly_payment',
    'realEstate_room_size',
    'realEstate_space_type',
    'realEstate_occupancy_periods',
    'realEstate_window_direction',
    'realEstate_elevator',
    'realEstate_building_type',
    'realEstate_built_date'
]
real_estate_detail = [
    'managementFees',
    'sink_status',
    'aircondition_status',
    'shoebox_status',
    'washingMachine_status',
    'refrigerator_status',
    'closet_status',
    'gasStoves_status',
    'bed_status',
    'cafe_status',
    'detail_info',
    'convenienceStore_status',
    'laundry_status',
    'supermarket_status',
    'busStation_status',
    'subway_status',
    'realEstateAgency_status'
]


def get_rscodes(file, region_url, driver):

    driver.get(region_url)
    content = driver.find_element(By.CSS_SELECTOR, ".simplebar-content")
    rss = content.find_elements(
        By.CSS_SELECTOR, 'ul')

    # pagination
    # page_list = content.find_elements(By.CSS_SELECTOR, "div")
    # if page_list != None:

    for ul in rss:
        items = []
        if "PremiumList" in ul.get_attribute("class"):
            print("premium")
            # items = ul.find_elements(
            #     By.CLASS_NAME, "styled__CardItem-sc-16s693f-6")
            tmp = ul.find_elements(By.CSS_SELECTOR, "li > div")
            for t in tmp:
                if "CardItem" in t.get_attribute("class"):
                    items.append(t)
        else:
            print("normal")
            tmp = ul.find_elements(
                By.CLASS_NAME, "styled__CardItem-sc-5dgg47-3")
            items += tmp

        for item in items:
            item.click()
            time.sleep(1)
            driver.switch_to.window(driver.window_handles[1])

            code = driver.current_url.split("/")[-1]
            file.write(f"{code}\n")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])


def extract_dabang_data():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    base_url = 'https://www.dabangapp.com/search/map?filters={"multi_room_type":[0,1,2],"selling_type":[0],"deposit_range":[0,999999],"price_range":[0,999999],"trade_range":[0,999999],"maintenance_cost_range":[0,999999],"room_size":[0,999999],"supply_space_range":[0,999999],"room_floor_multi":[1,2,3,4,5,6,7,-1,0],"division":false,"duplex":false,"room_type":[1,2],"use_approval_date_range":[0,999999],"parking_average_range":[0,999999],"household_num_range":[0,999999],"parking":false,"short_lease":false,"full_option":false,"built_in":false,"elevator":false,"balcony":false,"safety":false,"pano":false,"is_contract":false,"deal_type":[0,1]}&position={"location":[[127.0381186,37.543962],[127.1067832,37.5647836]],"center":[127.07245091941513,37.554373502088005],"zoom":14}&search={'
    last_url = '}&tab=all'

    with open('./gu_list.json') as file:
        json_obj = json.load(file)

    file = open("./dabang_rscodes.csv", "w")

    for reg, info in json_obj.items():
        print(info)
        region_url = f'{base_url}"id":"{info["id"]}","type":"{info["type"]}","name":"{info["name"]}"{last_url}'

        get_rscodes(file, region_url, driver)

    file.close()

    return


def category_price(e, dict1, dict2):
    li_price = e.find_elements(
        By.CSS_SELECTOR, 'div > :nth-child(2) > li')

    for li_elem in li_price:
        tmp = li_elem.find_elements(By.TAG_NAME, 'div')
        x = tmp[0].get_attribute('innerText')

        if "월세" in x:
            splitted = tmp[1].get_attribute('innerText').split("/")
            num = 0
            l = re.findall(r'\d+', splitted[0])
            if "억" in splitted[0]:
                l = re.findall(r'\d+', splitted[0])
                if len(l) == 2:
                    num = int(l[0])*100000000 + int(l[1])*10000
                elif len(l) == 1:
                    num = int(l[0])*100000000
            else:
                num = int(l[0])*10000

            dict1[ko_to_en["보증금"]], dict1[ko_to_en["월세"]] = num, int(
                re.findall(r'\d+', splitted[1])[0])*10000
        elif "관리비" in x:
            p_elem = tmp[1].find_element(By.CSS_SELECTOR, 'p:nth-child(1)')
            tmp = p_elem.get_attribute('innerText').strip()
            print(tmp)
            if tmp != "없음":
                dict2[ko_to_en["관리비"]] = int(
                    float(re.findall(r'\d+\.?\d*', tmp)[0])*10000)

    return (dict1, dict2)


def category_info(e, dict1, dict2):
    li_info = e.find_elements(
        By.CSS_SELECTOR, 'div > :nth-child(2) > li')

    for li_elem in li_info:
        tmp = li_elem.find_elements(By.TAG_NAME, 'div')

        x = tmp[0].get_attribute('innerText').strip()
        if x not in ko_to_en.keys():
            continue

        ex = ko_to_en[x]
        if x == "방향":
            dict1[ex] = tmp[1].get_attribute('innerText').replace(
                tmp[1].find_element(By.CSS_SELECTOR, 'span').get_attribute('innerText'), '').strip()
        elif ex in real_estate:
            dict1[ex] = tmp[1].get_attribute('innerText').strip()
        elif ex in real_estate_detail:
            dict2[ex] = tmp[1].get_attribute('innerText').strip()

    return dict1, dict2


def category_option(e, dict1, dict2):
    options = e.find_elements(
        By.CSS_SELECTOR, 'div')

    for option in options:
        op = option.find_elements(By.TAG_NAME, 'p')
        for np in op:
            p = np.get_attribute('innerText')
            if "없습니다" in p:
                return dict1, dict2

            if p not in ko_to_en:
                continue

            dict2[ko_to_en[p]] = True

    return dict1, dict2


def category_location(e, dict1, dict2):
    address = e.find_element(
        By.CSS_SELECTOR, 'div > div.styled__NewAddress-sc-8pfhii-4.diajmd > p').text

    dict1["realEstate_areaNumberAddress"] = address
    address_driver = webdriver.Chrome('chromedriver')
    time.sleep(2)
    d = "https://www.juso.go.kr/support/AddressMainSearch.do?searchKeyword="
    address_driver.get(d+address)
    ol = address_driver.find_elements(
        By.CSS_SELECTOR, '#searchAddress > div.container.support_search_list > div.search_list > ol > li')
    if len(ol) > 1:
        h = "unknown"
    else:
        try:
            h = address_driver.find_element(
                By.XPATH, '//*[@id="list1"]/div[1]/span[2]').text
        except:
            h = "unknown"

    dict1[ko_to_en["도로명주소"]] = h

    address_driver.close()

    try:
        buttons = e.find_elements(
            By.CSS_SELECTOR, 'div > div:nth-child(4) > div:nth-child(2) > button')
        for button in buttons:
            con = button.find_element(By.TAG_NAME, 'p').text
            if con in ko_to_en:
                dict2[ko_to_en[con]] = True
    except:
        print('no button')
        pass

    return dict1, dict2


def category_memo(e, dict1, dict2):
    detail_text = e.find_element(
        By.CSS_SELECTOR, 'div > div > p:nth-child(2)').text
    dict2["detail_info"] = detail_text

    return dict1, dict2


categories = {
    "price": category_price,
    "info": category_info,
    "option": category_option,
    "location": category_location,
    "memo": category_memo
}


def write_dict_to_csv(dictionary, filename):
    with open(filename, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=dictionary.keys())
        writer.writerow(dictionary)


def extract_details(code_list):
    driver = webdriver.Chrome()
    base_url = 'https://www.dabangapp.com/room'
    with open('realEstate.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=real_estate)
        writer.writeheader()
    with open('realEstateDetail.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=real_estate_detail)
        writer.writeheader()

    for code in code_list:
        item_url = f"{base_url}/{code}"

        driver.get(item_url)

        content = driver.find_elements(
            By.CSS_SELECTOR, '#content .styled__Content-sc-11huzff-5.eDgOXo > div')

        details = {}
        # elems = content.find_elements(By.TAG_NAME, "div")
        dict1 = {}
        for op in real_estate:
            dict1[op] = None
        dict2 = {}
        for op in real_estate_detail:
            dict2[op] = None
        for category in content:
            tmp = category.get_attribute('name')

            if tmp in categories.keys():
                dict1, dict2 = categories[tmp](category, dict1, dict2)

        print(dict1, dict2)
        write_dict_to_csv(dict1, "realEstate.csv")
        write_dict_to_csv(dict2, "realEstateDetail.csv")
