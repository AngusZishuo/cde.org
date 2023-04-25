import os
import re
import time

import pandas as pd
import pdfplumber
from pdfminer.pdfparser import PDFSyntaxError
from writer import write_csv


def join_csv():
    df1 = pd.read_csv('./cde.org_data/上市药品信息.csv', header=None, index_col=0, encoding='utf8')
    df2 = pd.read_csv('./cde.org_data/审批报告.csv', header=None, index_col=0, encoding='utf8')
    df_joined = df2.join(df1, how='left', rsuffix='f2')
    df_joined.to_csv('./cde.org_data/standard_审批报告.csv', header=False)


def wri_tit():
    csv_name = './cde.org_data/审批报告.csv'
    tit_list = ['受理号', '批准日期', '结构特征', '适应症等', '适应症领域', '完成的临床实验内容', '境内', '境外/其他', '境内I期', '境内II期', '境内III期', '境外I期',
                '境外II期', '境外III期', '附条件审批', '优先审评审批',
                '申报情况', '受理日期', 'Duration(批准-受理)', '上市许可申请前沟通交流申请', '研制和生产现场检查情况',
                '样品检验情况', '合规性评价', '临床药理学评价', '关键临床试验', '入组受试者（中国）', '入组受试者（全球）', '入组总人数', '入组完成人数',
                '上市后要求', '获益与风险评估', '商品名', '活性成分', '药品名称', '药品类型', '注册分类', '承办日期', '公示日期', '企业名称', 'PDF']
    if os.access(csv_name, os.F_OK):
        df = pd.read_csv(csv_name, header=None, names=tit_list)
        df.to_csv(csv_name, index=False)


def replacebracket(replacetext):
    return replacetext.replace("(", "").replace("（", "").replace(")", "").replace("）", "")


def standard_clinical_trial(clinical_trial, type):
    '''
    格式化完成的临床试验人数
    :param clinical_trial: 完成的临床试验人数字符串
    :return: 格式化后的数据,list
    '''

    # print(f'元数据----{clinical_trial}')
    global overseas
    active_clinical_trial_list = []
    active_clinical_trial_list2 = []
    clinical_trial_list = clinical_trial.split('\n')
    for s in clinical_trial_list:
        if re.findall('\.*[\u4e00-\u9fa5].*', s) or re.findall('.*■.*', s):
            active_clinical_trial_list.append(s)
    print(f'第一次处理后: {active_clinical_trial_list}')
    for i in range(0, len(active_clinical_trial_list)):
        if i > 0 and not re.findall('\.*[\u4e00-\u9fa5].*', active_clinical_trial_list[i]):
            check_flags = active_clinical_trial_list[i].split(' ')
            check_content = active_clinical_trial_list[i - 1].replace('境内', '').replace('境外', '').strip().split('期')
            if check_content[-1] == '':
                del check_content[-1]
            check_str = ''
            if check_flags and check_content and len(check_flags) <= len(check_content):
                if len(check_flags) < len(check_content):
                    for j in range(0, len(check_content) - len(check_flags)):
                        check_flags.append('■')
                preStr = ''
                if active_clinical_trial_list[i - 1].find('境内') >= 0:
                    preStr = '境内'
                if active_clinical_trial_list[i - 1].find('境外') >= 0:
                    preStr = '境外'
                for j in range(len(check_flags)):
                    if check_content[j].find('□') >= 0:
                        check_str = check_str + check_content[j].strip() + '期'
                    else:
                        check_str = check_str + check_flags[j] + check_content[j].strip() + '期'
                if preStr != '':
                    check_str = preStr + check_str
            active_clinical_trial_list2[len(active_clinical_trial_list2) - 1] = check_str
            continue
        active_clinical_trial_list2.append(active_clinical_trial_list[i])
    print(f'第二次处理后: {active_clinical_trial_list2}')
    try:
        if '境内' in active_clinical_trial_list2[0] or '期' in active_clinical_trial_list2[0]:
            if '■' in active_clinical_trial_list2[0]:
                domestic = '是'
            else:
                domestic = '否'
            if '■' in active_clinical_trial_list2[1]:
                overseas = '是'
            else:
                overseas = '否'
            active_clinical_trial_list2[0].replace('境内', '')
            domestic_phase_list = active_clinical_trial_list2[0].split('期')
            if '■' in domestic_phase_list[0]:
                domestic_phaseI = 'Y'
            else:
                domestic_phaseI = 'N'
            if '■' in domestic_phase_list[1]:
                domestic_phaseII = 'Y'
            else:
                domestic_phaseII = 'N'
            if '■' in domestic_phase_list[2]:
                domestic_phaseIII = 'Y'
            else:
                domestic_phaseIII = 'N'
        else:
            domestic = '否'
            domestic_phaseI = 'N'
            domestic_phaseII = 'N'
            domestic_phaseIII = 'N'
    except IndexError:
        domestic = '否'
        domestic_phaseI = 'N'
        domestic_phaseII = 'N'
        domestic_phaseIII = 'N'

    try:
        if len(active_clinical_trial_list2) >= 1 and '境外' in active_clinical_trial_list2[1] or '期' in \
                active_clinical_trial_list2[1]:
            active_clinical_trial_list2[1].replace('境外', '')
            overseas_phase_list = active_clinical_trial_list2[1].split('期')
            if '■' in overseas_phase_list[0]:
                overseas_phaseI = 'Y'
            else:
                overseas_phaseI = 'N'
            if '■' in overseas_phase_list[1]:
                overseas_phaseII = 'Y'
            else:
                overseas_phaseII = 'N'
            if '■' in overseas_phase_list[2]:
                overseas_phaseIII = 'Y'
            else:
                overseas_phaseIII = 'N'
        else:
            overseas = '否'
            overseas_phaseI = 'N'
            overseas_phaseII = 'N'
            overseas_phaseIII = 'N'
    except IndexError:
        overseas = '否'
        overseas_phaseI = 'N'
        overseas_phaseII = 'N'
        overseas_phaseIII = 'N'
    # print(domestic)
    # print(overseas)
    # print(domestic_phaseI)
    # print(domestic_phaseII)
    # print(domestic_phaseIII)
    # print(overseas_phaseI)
    # print(overseas_phaseII)
    # print(overseas_phaseIII)
    if type == 'standard':
        return [domestic, overseas, domestic_phaseI, domestic_phaseII, domestic_phaseIII, overseas_phaseI,
                overseas_phaseII,
                overseas_phaseIII]
    elif type == 'volunteer_size':
        return active_clinical_trial_list2


def get_pdf_text_data(file_name, pdf_line_list, allTableRow):
    approve_date = ''
    accepted_date = ''
    apply_before_marketing = ''
    compliance_evaluation = ''
    site_inspection = ''
    sample_check = ''
    sample_check_content = ''
    clinical_pharmacology_evaluation = ''
    pivotal_trials = ''
    benefit_risk = ''
    post_market_reqirement = ''
    indication = ''
    approval_condition = ''
    product_name = ''
    active_ingredients = ''
    structural_feature = ''
    indication_area = ''
    clinical_trial = ''  # 完成的临床试验内容
    approval_with_conditions = ''
    priority_approval = ''
    priority_approval_content = ''
    global_all_people = ''  # 入组总人数
    global_complete_people = ''  # 入组完成人数
    global_volunteer_size = ''  # [入组受试者（中国）]未处理
    china_volunteer_size = ''  # [入组受试者（全球）]未处理
    duration = ''  # [Duration(批准-受理)]未处理

    domestic = ''  # 境内
    overseas = ''  # 境外
    domestic_phaseI = ''
    domestic_phaseII = ''
    domestic_phaseIII = ''
    overseas_phaseI = ''
    overseas_phaseII = ''
    overseas_phaseIII = ''

    # 受理号
    slh_number = file_name.split("-")[0]
    # print(f'受理号:{slh_number}')
    i = 0
    line = pdf_line_list[i]

    while line:
        # 批准日期
        if re.match("^批准日期.*$", line):
            approve_date = line.strip().replace(":", "@").replace("：", "@").split("@")[1]
            approve_date = approve_date.replace('年', '/').replace('月', '/').replace('日', '').replace(' ', '')
            # print(f'批准日期:{approve_date}')
        if line.strip() == "一、基本信息":
            while line:
                # 受理日期
                if line.split() and re.match("受理日期.*[0-9]+", line):
                    accepted_date = line.strip().replace(":", "@").replace("：", "@").split('@')[1]
                    accepted_date = accepted_date.replace('年', '/').replace('月', '/').replace('日', '').replace(' ',
                                                                                                               '').replace(
                        '-', '/')
                    # print(f'受理日期:{accepted_date}')

                # 上市许可前沟通交流申请
                if line.split() and re.match("上市.*申请前.*交流.*", line.strip()):
                    apply_before_marketing = "有"
                    # print(f'上市许可前沟通交流申请:{apply_before_marketing}')

                # #研制和生产现场检查情况,样品检验情况,合规性评价 处理  site_inspection,sample_check,compliance_evaluation
                if line.split() and re.match("['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*现场.*查情况",
                                             replacebracket(line)):
                    i = i + 1
                    if i >= len(pdf_line_list):
                        break
                    line = pdf_line_list[i]
                    live_check_content = ""
                    while line and not re.match("['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*样品检验情况",
                                                replacebracket(line)):
                        if line.split():
                            live_check_content = live_check_content + line
                        i = i + 1
                        if i >= len(pdf_line_list):
                            break
                        line = pdf_line_list[i]

                    if line.split() and re.match("['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*样品检验情况",
                                                 replacebracket(line)):
                        sample_check_content = ""
                        while line and not re.match(
                                "['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*合规性评价",
                                replacebracket(line)) and not re.match(
                            "['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*临床.*核查",
                            replacebracket(line)):
                            if line.split():
                                sample_check_content = sample_check_content + line
                            i = i + 1
                            if i >= len(pdf_line_list):
                                break
                            line = pdf_line_list[i]
                    if line.split() and (
                            re.match("['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*合规性评价",
                                     replacebracket(line)) or
                            re.match("['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*临床.*核查",
                                     replacebracket(line))):
                        i = i + 1
                        if i >= len(pdf_line_list):
                            break
                        line = pdf_line_list[i]
                        compliance_evaluation_content = ""
                        while line and not re.match(
                                "['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*综合审评意见",
                                replacebracket(line)):
                            if line.split():
                                compliance_evaluation_content = compliance_evaluation_content + line
                            i = i + 1
                            if i >= len(pdf_line_list):
                                break
                            line = pdf_line_list[i]
                        if re.match("临床核查", compliance_evaluation_content):
                            compliance_evaluation = "临床核查"
                        else:
                            compliance_evaluation = compliance_evaluation_content
                        # print(f'合规性评价:{compliance_evaluation}')
                    if re.match(".*不适用", live_check_content):
                        site_inspection = "无"
                    else:
                        site_inspection = "有"

                    # print(f'研制和生产现场检查情况:{site_inspection}')
                    if re.match(".*不适用", sample_check_content):
                        sample_check = "无"
                    else:
                        sample_check = "有"

                    # print(f'样品检验情况:{sample_check}')

                # 临床药理学评价,关键临床试验 处理  clinical_pharmacology_evaluation pivotal_trials
                if line.split() and re.match(
                        "['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*临床.*药理.*评价",
                        replacebracket(line)):
                    while line and not re.match(
                            "['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*有效性.*评价",
                            replacebracket(line)):
                        if line.split():
                            clinical_pharmacology_evaluation = clinical_pharmacology_evaluation + line
                        i = i + 1
                        if i >= len(pdf_line_list):
                            break
                        line = pdf_line_list[i]
                    # print(f'临床药理学评价:{clinical_pharmacology_evaluation}')
                    i = i + 1
                    if i >= len(pdf_line_list):
                        break
                    line = pdf_line_list[i]
                    pivotal_trials_content = ""
                    while line and not re.match(
                            "['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*安全.*评价",
                            replacebracket(line)) and not re.match(
                        "['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*风险.*分析.*控制",
                        replacebracket(line)):
                        if line.split():
                            pivotal_trials_content = pivotal_trials_content + line.strip()
                        i = i + 1
                        if i >= len(pdf_line_list):
                            break
                        line = pdf_line_list[i]
                    if (re.search("关键.*?临床试验.*?(；|。)", pivotal_trials_content)):
                        pivotal_trials = re.search("关键.*?临床试验.*?(；|。)", pivotal_trials_content).group()
                    # print(f'关键临床试验:{pivotal_trials}')

                # 获益与风险评估 处理 benefit_risk
                if line.split() and re.match("['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*获益.*风险",
                                             replacebracket(line)):
                    i = i + 1
                    if i >= len(pdf_line_list):
                        break
                    line = pdf_line_list[i]
                    while line and not re.match(
                            "['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*说明书.*审核",
                            replacebracket(line)) and not re.match(
                        "['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*评价过程中发现的主要问题及处理",
                        replacebracket(line)) and not re.match(
                        "['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*处理意见",
                        replacebracket(line)) and not re.match(
                        "['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*三合一审评情况", replacebracket(line)):
                        if line.strip() != "内容" and line.split():
                            benefit_risk = benefit_risk + line
                        i = i + 1
                        if i >= len(pdf_line_list):
                            break
                        line = pdf_line_list[i]

                    # print(f'获益与风险评估:{benefit_risk}')
                # 上市后要求 处理 post_market_reqirement
                if line.split() and re.match(
                        "['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*上市.*后.*要求",
                        replacebracket(line)):
                    i = i + 1
                    if i >= len(pdf_line_list):
                        break
                    line = pdf_line_list[i]
                    while line and not re.match(
                            "['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*上市.*后.*安全",
                            replacebracket(line)) and not re.match(
                        "['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',0-9].*上市.*后.*风险控制",
                        replacebracket(line)):
                        if line.strip() != "内容" and line.split():
                            post_market_reqirement = post_market_reqirement + line
                        i = i + 1
                        if i >= len(pdf_line_list):
                            break
                        line = pdf_line_list[i]

                    # print(f'上市后要求:{post_market_reqirement}')
                i = i + 1
                if i >= len(pdf_line_list):
                    break
                line = pdf_line_list[i]
        i = i + 1
        if i >= len(pdf_line_list):
            break
        line = pdf_line_list[i]

    # ----------------------------------------------------------------------------------------------------根据表格提取数据
    # 遍历二维数组获取数据
    for tableRow in allTableRow:

        if len(tableRow) == 1:
            continue
        columnName = tableRow[0]

        columnContent = tableRow[1]
        if columnName is None or columnName == '':
            continue
        if columnContent is None or columnContent == '':
            continue
        # 结构特征处理  structural_feature
        if re.match("结构特征", columnName) and columnName.split():
            checkedStr = ''
            if columnContent.strip().find("√") >= 0:
                checkedStr = "√"
            if columnContent.strip().find("") >= 0:
                checkedStr = ""
            if columnContent.strip().find("■") >= 0:
                checkedStr = "■"
            if columnContent.strip().find("☑") >= 0:
                checkedStr = "☑"
            if checkedStr != '':
                checkItems = columnContent.split('\n')
                for i in range(0, len(checkItems)):
                    if checkItems[i].strip().find(checkedStr) >= 0:
                        checkItem = checkItems[i].strip().replace(checkedStr, "").strip()
                        if checkItem.find("其他", 0, 5) >= 0:
                            for j in range(i + 1, len(checkItems)):
                                checkItem = checkItem + checkItems[j]
                            structural_feature = checkItem
                        else:
                            structural_feature = checkItem
                        break
        # 适应症等 适应症领域 处理  indication
        if columnName.strip() == "适应症" or columnName.strip() == "适应症等" or re.match("适应症/功能主治.*", columnName.strip()):
            indication = columnContent.replace('\n', '')
            if re.match("瘤|癌", indication):
                indication_area = "抗肿瘤药物"
        # 完成的临床试验内容 处理  clinical_trial
        if columnName.strip().replace('\n', '') == "完成的临床试验内容" or columnName.strip().replace('\n', '') == "完成的临床试验":
            clinical_trial = columnContent.replace("√", "■").replace("", "■").replace("■", "■").replace("☑",
                                                                                                         "■").replace(
                '\uf0a3', '□').replace('\uf0fe', '■').replace('▇', '■')
        # 附条件审批 处理  approval_with_conditions
        if columnName.strip() == "附条件批准":
            if columnContent.strip().find("√") >= 0 or columnContent.strip().find(
                    "") >= 0 or columnContent.strip().find(
                "■") >= 0 or columnContent.strip().find("☑") >= 0:
                try:
                    approval_with_conditions = \
                        (columnContent.strip().replace("√", "@").replace("", "@").replace("■", "@").replace("☑",
                                                                                                             "@").split(
                            '@')[1]).split(" ")[0]
                except:
                    approval_with_conditions = columnContent.strip()
        # 优先审评审批 优先审评审批内容 处理 priority_approval  priority_approval_content
        if columnName.strip() == "优先审评审批" or columnName.strip() == "优先审评":
            checkStr = columnContent.split('\n')[0]
            if checkStr.strip().find("√") >= 0 or checkStr.strip().find("") >= 0 or checkStr.strip().find(
                    "■") >= 0 or checkStr.strip().find("☑") >= 0:
                try:
                    priority_approval = \
                        (checkStr.strip().replace("√", "@").replace("", "@").replace("■", "@").replace("☑",
                                                                                                        "@").split(
                            '@')[1]).split(" ")[0]
                except:
                    priority_approval = checkStr
            # 优先审评审批内容 处理 priority_approval_content 将是否选项所在行除外的所有内容作为优先审评审批内容
            if priority_approval == "是" and columnContent.find('\n') >= 0:
                priority_approval_content = columnContent[(columnContent.index('\n') + 1):]
                if priority_approval_content.find('注：') >= 0:
                    priority_approval_content = priority_approval_content[0:priority_approval_content.index('注：') - 1]
        # 申报情况 处理 approval_condition
        if columnName.strip() == "申报情况":
            try:
                approval_condition = \
                    (columnContent.strip().replace("√", "@").replace("", "@").replace("■", "@")
                        .replace("☑", "@").split('@')[1]).split(" ")[0]
                approval_condition = approval_condition.replace("□", "")
            except:
                approval_condition = ''
        # 商品名  处理 product_name
        if re.match("商品名", columnName) or re.match("通用名（中/英文）", columnName):
            product_name = columnContent.strip()
        # 活性成分 处理 active_ingredients
        if re.match("化学名称（中/英文）", columnName) or re.match("活性成.*(分|份)", columnName):
            active_ingredients = columnContent.strip()

    standard_clinical_trial_list = standard_clinical_trial(clinical_trial, type='standard')
    domestic = standard_clinical_trial_list[0]
    overseas = standard_clinical_trial_list[1]
    domestic_phaseI = standard_clinical_trial_list[2]
    domestic_phaseII = standard_clinical_trial_list[3]
    domestic_phaseIII = standard_clinical_trial_list[4]
    overseas_phaseI = standard_clinical_trial_list[5]
    overseas_phaseII = standard_clinical_trial_list[6]
    overseas_phaseIII = standard_clinical_trial_list[7]

    # 入组总人数
    pdf_line_list_text = ''.join(pdf_line_list)
    global_all_people = re.search("入组 [0-9]* 例", pdf_line_list_text)
    if global_all_people == None:
        global_all_people = ''
    else:
        global_all_people = global_all_people.group()

    # 入组受试者中国/全球
    active_clinical_trial_list = standard_clinical_trial(clinical_trial, type='volunteer_size')
    try:
        if '■' in active_clinical_trial_list[0] and '■' not in active_clinical_trial_list[1]:
            china_volunteer_size = global_all_people
            global_volunteer_size = ''

        elif '■' in active_clinical_trial_list[1] and '■' not in active_clinical_trial_list[0]:
            china_volunteer_size = ''
            global_volunteer_size = global_all_people
    except IndexError:
        china_volunteer_size = ''
        global_volunteer_size = ''

    report_text_data_list = []
    report_text_data_list.append(slh_number)  # 受理号
    report_text_data_list.append(approve_date)
    report_text_data_list.append(structural_feature)
    report_text_data_list.append(indication)
    report_text_data_list.append(indication_area)
    report_text_data_list.append(clinical_trial)
    report_text_data_list.append(domestic)
    report_text_data_list.append(overseas)
    report_text_data_list.append(domestic_phaseI)
    report_text_data_list.append(domestic_phaseII)
    report_text_data_list.append(domestic_phaseIII)
    report_text_data_list.append(overseas_phaseI)
    report_text_data_list.append(overseas_phaseII)
    report_text_data_list.append(overseas_phaseIII)
    report_text_data_list.append(approval_with_conditions)
    report_text_data_list.append(priority_approval)
    report_text_data_list.append(approval_condition.replace('□', ''))
    report_text_data_list.append(accepted_date)
    report_text_data_list.append(duration)
    report_text_data_list.append(apply_before_marketing)
    report_text_data_list.append(site_inspection)
    report_text_data_list.append(sample_check)
    report_text_data_list.append(compliance_evaluation)
    report_text_data_list.append(clinical_pharmacology_evaluation)
    report_text_data_list.append(pivotal_trials)
    report_text_data_list.append(china_volunteer_size)
    report_text_data_list.append(global_volunteer_size)
    report_text_data_list.append(global_all_people)
    report_text_data_list.append(global_complete_people)
    report_text_data_list.append(post_market_reqirement)
    report_text_data_list.append(benefit_risk)
    report_text_data_list.append(product_name.replace('\n', ''))
    report_text_data_list.append(active_ingredients.replace('\n', ''))
    # report_text_data_list.append(priority_approval_content)
    return report_text_data_list


def get_all_pdf_files_data():
    # w_tit()
    global this_pdf
    for filename in os.listdir(r"./cde.org_data/files/"):
        if '说明书' in filename:
            continue
        print(f'------------------ {filename}')
        try:
            this_pdf = pdfplumber.open(f'./cde.org_data/files/{filename}')
        except PDFSyntaxError:
            # pdf下载文件损坏，暂时先跳过
            continue
        allTableRow = []  # 定义数组存储所有表格内容，每个元素是一维数组，代表了表格的每一行
        for pageObj in this_pdf.pages:
            tables = pageObj.extract_tables()
            if len(tables) > 0:
                for table in tables:
                    if len(table) > 0:
                        for row in table:
                            if len(row) > 0:
                                allTableRow.append(row)
        # print(allTableRow)
        # 如果表格存在跨页（一维数组的第一个元素是空串），则将跨页的表格内容合并在一起
        for i in range(0, len(allTableRow)):
            if i == 0: continue
            if allTableRow[i][0] == '' and allTableRow[i - 1][0] and len(allTableRow[i]) == len(allTableRow[i - 1]):
                for j in range(1, len(allTableRow[i - 1])):
                    if allTableRow[i - 1][j] and allTableRow[i][j]:
                        allContent = allTableRow[i - 1][j] + '\n' + allTableRow[i][j]
                        allTableRow[i - 1][j] = allContent
        # 读取PDF所有行
        pdf_text = ''
        for page in this_pdf.pages:
            this_page_text = page.extract_text()
            this_page_text_list = this_page_text.split('\n')
            # 删除页码
            del this_page_text_list[-1]
            this_page_text = '\n'.join(this_page_text_list)
            pdf_text += this_page_text + '\n'
        # 切割后得到list
        pdf_line_list = pdf_text.split('\n')
        # 获取文本数据
        pdf_text_data = get_pdf_text_data(filename, pdf_line_list, allTableRow)
        pdf_data_list = []
        pdf_data_list.append(pdf_text_data)
        write_csv('./cde.org_data/审批报告.csv', pdf_data_list)
        this_pdf.close()
    print('------------------ 结束 -----------------------')


# get_all_pdf_files_data()
time.sleep(10)
join_csv()
time.sleep(10)
wri_tit()
