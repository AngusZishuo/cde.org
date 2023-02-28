import csv
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from pySelenium import PySelenium

'''
firefox:V55.0
selenium:V3.141.0
'''


class Run(PySelenium):
    # 翻页
    def turn_pages(self):
        # 优先审评按钮
        target_button1 = (By.XPATH, './/ul[@class="etcd_nav_ul"]/li[5]')
        # 突破性治疗按钮
        target_button2 = (By.XPATH, './/ul[@class="etcd_nav_ul"]/li[6]')
        # 下一页按钮
        next_button = (By.XPATH,
                       './/div[@class="mc_source"]/div[5]//div[@class="layui-tab-item layui-show"]//div/a[@class="layui-laypage-next"]')
        # 总页数
        page_all = 138
        # 点击审评按钮
        time.sleep(3)
        self.click_loc(target_button1)
        time.sleep(10)

        for this_page_number in range(page_all + 1):
            print('>' * 20 + f"当前正在打印第{this_page_number + 1}页数据")
            # 取数据
            self.getData()
            time.sleep(0.5)
            # 点击下一页按钮
            self.locator(next_button).click()
            time.sleep(0.5)

    def getData(self):
        tr_number = 10
        td_number = 8
        table_all_list = []
        # 遍历table_tr
        for tr_num in range(1, tr_number + 1):
            print(f'打印第{tr_num}条数据')
            # 每一行的list
            table_info_list = []
            # 遍历table_td
            for td_num in range(1, td_number + 1):
                # 取每行数据
                table_info = (By.XPATH,
                              f'.//div[@class="mc_source"]/div[5]//table/tbody[@id="includePriorityTbody"]/tr[{tr_num}]/td[{td_num}]')
                table_info = self.locator(table_info).text
                # 取到后保存在每一行的list中
                table_info_list.append(table_info)
            # 执行双击操作
            dialog_up_button = self.driver.find_element_by_xpath(
                f'.//div[@class="mc_source"]/div[5]//table/tbody[@id="includePriorityTbody"]/tr[{tr_num}]')
            self.find(dialog_up_button)  # 高亮显示点击的元素
            ActionChains(self.driver).double_click(dialog_up_button).perform()
            time.sleep(0.5)
            # 取弹框数据
            dialog_up = (By.XPATH, './/div/div[@id="reviewTaskPublicityDetail"]/table/tbody/tr[6]/td[2]')
            dialog_up_info = self.locator(dialog_up).get_attribute('innerHTML')
            # 点击弹框关闭
            dialog_close_button = (
                By.XPATH, './/div/div[@id="reviewTaskPublicityDetail"]/parent::div/parent::div/span/a')
            self.locator(dialog_close_button).click()
            table_info_list.append(dialog_up_info)
            # 将每一行的list保存在元数据中
            table_all_list.append(table_info_list)
        # 调取写入函数,写入数据
        self.write_csv('./优先审评公示.csv', table_all_list)


if __name__ == '__main__':
    url = 'https://d3d3LmNkZS5vcmcuY24=/main/xxgk/listpage/9f9c74c73e0f8f56a8bfbc646055026d'
    browser = webdriver.Firefox()
    browser.implicitly_wait(40)
    start = Run(browser)
    # 打开url
    start.visit_url(url)
    start.maxwin()
    time.sleep(3)
    # 取数据
    start.turn_pages()
