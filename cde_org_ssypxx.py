import csv
import os
import time
import pandas as pd
import pdfplumber
from pdfminer.pdfparser import PDFSyntaxError
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from pySelenium import PySelenium
from writer import write_csv


class Run(PySelenium):
    def del_file(self,filepath):
        files = os.listdir(filepath)
        for file in files:
            if '.' in file:
                suffix = file.split('.')[-1]
                # 指定删除part的后缀名文件
                if suffix == 'part':
                    os.remove(os.path.join(filepath, file))

    def check_pdf_file(self, fileid, acceptid, slh, filename):
        if f'{slh}-{filename}' not in os.listdir(r"./data/files/"):
            # 文件不存在，下载文件
            self.download_this_file(fileid, acceptid, slh, filename)
        else:
            try:
                # 打开文件，检查文件有效性
                with pdfplumber.open(f'./data/files/{slh}-{filename}') as this_pdf:
                    this_pdf.close()
                    pass
            except PDFSyntaxError:
                # 文件无效，删除文件，重新下载
                os.remove(f'./data/files/{slh}-{filename}')
                self.download_this_file(fileid, acceptid, slh, filename)
            else:
                # 文件有效，不需要下载
                pass
        self.del_file('./data/files/')

    def csv_deduplication(self, file):
        '''
        Args: csv文件去重
            file: 文件名称
        '''
        df = pd.read_csv(file, header=0, encoding='utf-8')
        datalist = df.drop_duplicates()
        datalist.to_csv(file, encoding='utf-8', header=None, index=None)

    def read_first_column(self):
        with open('./data/附件详情.csv', 'r', encoding='utf-8 ') as file:
            reader = csv.reader(file)
            column = [row[0] for row in reader]
        return column

    def download_this_file(self, fileid, acceptid, slh, filename):
        # 下载文件
        # ...
        if f'{slh}-{filename}' not in os.listdir(r"./data/files/"):
            # 文件不存在，下载文件
            self.driver.execute_script(
                f"defaultObj.methods.downloadFile('{fileid}','{acceptid}','{slh}-{filename}')")

    def download_all_file(self):
        file_list = self.read_first_column()
        for file_name in file_list:
            file_name = file_name.split('|')
            self.download_this_file(file_name[0], file_name[1], file_name[2], file_name[3])
            time.sleep(3)

    def turn_pages(self):
        # 优先审评按钮
        global slh, drug_name, register_type, gs_date, drug_type, cb_date, firm_name
        # if not os.path.exists('./data/附件详情.csv'):
        #     open('./data/附件详情.csv', mode='w')
        # else:
        #     pass
        target_button1 = (By.XPATH, '//ul[@class="etcd_nav_ul"]/li[11]')
        self.click_loc(target_button1)
        time.sleep(3)
        page_all = 2000
        tr_number = 10
        for this_page_number in range(page_all + 1):
            time.sleep(3)
            # 遍历数据
            for tr_index in range(1, tr_number + 1):
                ctr_list = []
                # 执行双击操作
                dialog_up_button = self.driver.find_element(By.XPATH, f'//*[@id="listDrugInfoTbody"]/tr[{tr_index}]')
                self.find(dialog_up_button)  # 高亮显示点击的元素
                ActionChains(self.driver).double_click(dialog_up_button).perform()
                # 打开新窗口
                self.switch_to(-1)
                slh = self.get_locator('//td[contains(text(),"受理号")]/following::td[1]')
                drug_name = self.get_locator('//td[contains(text(),"药品名称")]/following::td[1]')
                drug_type = self.get_locator('//td[contains(text(),"药品类型")]/following::td[1]')
                register_type = self.get_locator('//td[contains(text(),"注册分类")]/following::td[1]')
                cb_date = self.get_locator('//td[contains(text(),"承办日期")]/following::td[1]')
                gs_date = self.get_locator('//td[contains(text(),"公示日期")]/following::td[1]')
                firm_name = self.get_locator('//td[contains(text(),"企业名称")]/following::td[1]')

                time.sleep(1)
                ###附件
                fj_index = len(self.driver.find_elements(By.XPATH, './/a[@href="javascript:;"]'))
                fj_name = []
                fj_list = []
                for i in range(1, fj_index + 1):
                    try:
                        fileid = self.driver.find_element(By.XPATH,
                                                          f'//td[contains(text(),"相关附件信息")]/following::td[{i}]/a').get_attribute(
                            'data-fileid')
                        acceptid = self.driver.find_element(By.XPATH,
                                                            f'//td[contains(text(),"相关附件信息")]/following::td[{i}]/a').get_attribute(
                            'data-acceptid')
                        filename = self.driver.find_element(By.XPATH,
                                                            f'//td[contains(text(),"相关附件信息")]/following::td[{i}]/a').get_attribute(
                            'data-filename')
                    except:
                        time.sleep(5)
                        fileid = self.driver.find_element(By.XPATH,
                                                          f'//td[contains(text(),"相关附件信息")]/following::td[{i}]/a').get_attribute(
                            'data-fileid')
                        acceptid = self.driver.find_element(By.XPATH,
                                                            f'//td[contains(text(),"相关附件信息")]/following::td[{i}]/a').get_attribute(
                            'data-acceptid')
                        filename = self.driver.find_element(By.XPATH,
                                                            f'//td[contains(text(),"相关附件信息")]/following::td[{i}]/a').get_attribute(
                            'data-filename')
                    fj_list.append(filename)
                    # if '说明书' in filename:
                    #     continue
                    if i >= 1:
                        continue
                    fj_name.append([f'{fileid}|{acceptid}|{slh}|{filename}'.replace('\"', '')])
                    if f'{fileid}|{acceptid}|{slh}|{filename}'.replace('\"', '') not in self.read_first_column():
                        print(fj_name)
                        write_csv('./data/附件详情.csv', fj_name)
                fj = '/ '.join(fj_list)
                info_list = [slh, drug_name, drug_type, register_type, cb_date, gs_date, firm_name, fj]
                ctr_list.append(info_list)
                # 关闭当前窗口并返回之前的页面
                self.close_this_page()
                self.switch_to(0)
                write_csv('./data/上市药品信息.csv', ctr_list)
            next_button = self.driver.find_element(By.XPATH,
                                                   './/div[@class="mc_source"]/div[11]//a[contains(text(),"下一页")]')
            next_button_class=next_button.get_attribute('class')
            # 下一页
            if next_button_class == 'layui-laypage-next layui-disabled':
                break
            next_button.click()

        # self.csv_deduplication('./data/附件详情.csv')
        # print('附件详情.csv 去重')
        # self.csv_deduplication('./data/上市药品信息.csv')
        # print('上市药品信息.csv 去重')


if __name__ == '__main__':
    url = 'https://www.cde.org.cn/main/xxgk/listpage/b40868b5e21c038a6aa8b4319d21b07d'
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    # 下载文件地址,要求绝对路径
    profile.set_preference("browser.download.dir", "D:\\spider\\project_folder\\pythonProject\\data\files\\")
    profile.set_preference("browser.download.manager.alertOnEXEOpen", False)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "application/msword, application/csv, application/ris, text/csv, image/png, application/pdf, text/html, text/plain, application/zip, application/x-zip, application/x-zip-compressed, application/download, application/octet-stream")
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.manager.focusWhenStarting", False)
    profile.set_preference("browser.download.useDownloadDir", True)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.download.manager.alertOnEXEOpen", False)
    profile.set_preference("browser.download.manager.closeWhenDone", True)
    profile.set_preference("browser.download.manager.showAlertOnComplete", False)
    profile.set_preference("browser.download.manager.useWindow", False)
    profile.set_preference("services.sync.prefs.sync.browser.download.manager.showWhenStarting", False)
    profile.set_preference("pdfjs.disabled", True)
    driver = webdriver.Firefox(firefox_profile=profile)
    driver.implicitly_wait(20)
    start = Run(driver)
    # 打开url
    start.visit_url(url)
    start.maxwin()
    time.sleep(15)
    # 取数据
    # start.turn_pages()
    # 下文件
    start.csv_deduplication('./data/上市药品信息.csv')
    start.csv_deduplication('./data/附件详情.csv')
    start.download_all_file()
    start.driver.quit()