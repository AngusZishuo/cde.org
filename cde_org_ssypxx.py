import csv
import os
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from pySelenium import PySelenium
from writer import write_csv


class Run(PySelenium):
    def turn_pages(self):
        # 优先审评按钮
        global slh, drug_name, register_type, gs_date, drug_type, cb_date, firm_name
        target_button1 = (By.XPATH, '//ul[@class="etcd_nav_ul"]/li[11]')
        next_button = (By.XPATH, '//a[@class="layui-laypage-next"]')
        time.sleep(3)
        self.click_loc(target_button1)
        time.sleep(3)
        page_all = 96
        tr_number = 10
        time.sleep(30)
        for this_page_number in range(page_all + 1):
            # 遍历数据
            for tr_index in range(1, tr_number + 1):
                ctr_list = []
                # 执行双击操作
                for i in range(10):
                    try:
                        dialog_up_button = self.driver.find_element(By.XPATH,
                                                                    f'//*[@id="listDrugInfoTbody"]/tr[{tr_index}]')
                        self.find(dialog_up_button)  # 高亮显示点击的元素
                        ActionChains(self.driver).double_click(dialog_up_button).perform()
                        break
                    except:
                        pass
                # 打开新窗口
                self.switch_to(-1)
                slh = self.get_locator('//td[contains(text(),"受理号")]/following::td[1]')
                drug_name = self.get_locator('//td[contains(text(),"药品名称")]/following::td[1]')
                drug_type = self.get_locator('//td[contains(text(),"药品类型")]/following::td[1]')
                register_type = self.get_locator('//td[contains(text(),"注册分类")]/following::td[1]')
                cb_date = self.get_locator('//td[contains(text(),"承办日期")]/following::td[1]')
                gs_date = self.get_locator('//td[contains(text(),"公示日期")]/following::td[1]')
                firm_name = self.get_locator('//td[contains(text(),"企业名称")]/following::td[1]')

                ###附件
                fj_index = len(self.driver.find_elements(By.XPATH, './/a[@href="javascript:;"]'))
                fj_list = []
                for i in range(1, fj_index + 1):
                    fileid = self.driver.find_element(By.XPATH,
                                                      f'//td[contains(text(),"相关附件信息")]/following::td[{i}]/a').get_attribute(
                        'data-fileid')
                    acceptid = self.driver.find_element(By.XPATH,
                                                        f'//td[contains(text(),"相关附件信息")]/following::td[{i}]/a').get_attribute(
                        'data-acceptid')
                    filename = self.driver.find_element(By.XPATH,
                                                        f'//td[contains(text(),"相关附件信息")]/following::td[{i}]/a').get_attribute(
                        'data-filename')

                    # 下载附件
                    fj_list.append(filename)
                    self.driver.execute_script(
                        f"defaultObj.methods.downloadFile('{fileid}','{acceptid}','{slh}-{filename}')")
                    time.sleep(1)
                fj = '/ '.join(fj_list)
                info_list = [slh, drug_name, drug_type, register_type, cb_date, gs_date, firm_name, fj]
                ctr_list.append(info_list)
                # 关闭当前窗口并返回之前的页面
                self.close()
                self.switch_to(0)
                write_csv('./上市药品信息.csv', ctr_list)
            # 下一页
            self.locator(next_button).click()
            time.sleep(1)


url = 'https://www.cde.org.cn/main/xxgk/listpage/b40868b5e21c038a6aa8b4319d21b07d'

driver = webdriver.Firefox()
driver.switch_to.frame("x-URS-iframe")
driver.implicitly_wait(20)
start = Run(driver)
# 打开url
start.visit_url(url)
start.maxwin()
# 取数据
start.turn_pages()
