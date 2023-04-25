import os
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from pySelenium import PySelenium
import pandas as pd

'''
firefox:V55.0
selenium:V3.141.0
'''


class Run(PySelenium):
    def wri_tit(self):
        csv_path = './data/优先审评公示.csv'
        tit_list = ['受理号', '药品名称', '注册申请人', '承办日期', '申请日期', '公示日期', '状态', '拟定适应症（或功能主治）']
        if os.access(csv_path, os.F_OK):
            df = pd.read_csv(csv_path, header=None, names=tit_list)
            df.to_csv(csv_path, index=False)

    def turn_pages(self):
        # Locators
        ETCD_NAV_LI = (By.XPATH, './/ul[@class="etcd_nav_ul"]/li[5]')
        LAZY_PAGE_NEXT = (By.XPATH, './/div[5]//a[contains(text(),"下一页")]')
        # Click the "优先审评" button
        self.click_loc(ETCD_NAV_LI)
        time.sleep(3)
        for page_number in range(1, 2000):
            print(f"{'>' * 20} 当前正在打印第{page_number}页数据")
            # Get data
            table_all_list = self.getData()
            # Write data to file
            self.write_csv('./data/优先审评公示.csv', table_all_list)
            # Click the next page button

            next_button = self.locator(LAZY_PAGE_NEXT)
            next_button_class=next_button.get_attribute('class')
            if next_button_class == 'layui-laypage-next layui-disabled':
                break
            next_button.click()
            time.sleep(3)

            time.sleep(0.5)

    def getData(self):
        time.sleep(5)
        table_all_list = []
        # Find all rows in the table
        table_tr = self.driver.find_elements(By.XPATH,
                                             './/div[@class="mc_source"]/div[5]//table/tbody[@id="includePriorityTbody"]/tr')

        # 遍历table_tr
        for tr in table_tr:
            print(f'打印第{table_tr.index(tr) + 1}条数据')
            # Get data from the first 7 columns in the current row
            table_info_list = [td.text for td in tr.find_elements(By.XPATH, './/td[position()<10]')]
            del table_info_list[0]
            print(table_info_list)
            ActionChains(self.driver).double_click(tr).perform()
            time.sleep(0.5)
            # Get data from the popup dialog
            dialog_up = self.driver.find_element(By.XPATH,
                                                 './/div/div[@id="reviewTaskPublicityDetail"]/table/tbody/tr[6]/td[2]').get_attribute(
                'innerHTML')

            for i in range(10):

                try:
                    # 点击弹框关闭
                    self.driver.find_element(By.XPATH,
                                             './/div/div[@id="reviewTaskPublicityDetail"]/parent::div/parent::div/span/a').click()
                    break
                except:
                    time.sleep(2)
                    pass

            table_info_list.append(dialog_up)
            # Save the current row data to the list of all data
            table_all_list.append(table_info_list)
        return table_all_list


if __name__ == '__main__':
    url = 'https://www.cde.org.cn/main/xxgk/listpage/9f9c74c73e0f8f56a8bfbc646055026d'
    browser = webdriver.Firefox()
    browser.implicitly_wait(20)
    start = Run(browser)
    start.visit_url(url)
    start.maxwin()
    time.sleep(3)
    # 取数据
    start.turn_pages()
    start.wri_tit()
