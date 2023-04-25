import csv

sp_path = './data/standard_审批报告.csv'
yx_path = './data/优先审评公示.csv'
tp_path = './data/突破性治疗公示.csv'
ss_path = './data/上市药品信息.csv'


def read_first_column(file_path):
    with open(file_path, 'r', encoding='utf-8 ') as file:
        reader = csv.reader(file)
        column = [row[0] for row in reader]
    del column[0]
    return set(column)


ss = read_first_column(ss_path)
sp = read_first_column(sp_path)
yx = read_first_column(yx_path)
tp = read_first_column(tp_path)
#
tp_eq_sp = []
for i in tp:
    if i in sp:
        tp_eq_sp.append(i)
print(f'突破性治疗受理号在审批报告中存在的有:    {tp_eq_sp}\n  共{len(tp_eq_sp)}条')
print('----------------------------------------------------------------------------')
yx_eq_sp = []
for i in yx:
    if i in sp:
        yx_eq_sp.append(i)
print(f'优先审评公示受理号在审批报告中存在的有:    {yx_eq_sp}\n  共{len(yx_eq_sp)}条')
print('----------------------------------------------------------------------------')
tp_eq_yx = []
for i in tp:
    if i in yx:
        tp_eq_yx.append(i)
print(f'突破性治疗受理号在优先审评公示中存在的有:    {tp_eq_yx}\n  共{len(tp_eq_yx)}条')
print('----------------------------------------------------------------------------')
tpandyx_eq_sp = []
for i in tp:
    if i in yx and i in sp:
        tpandyx_eq_sp.append(i)
print(f'受理号在三个文件中都存在的有:    {tpandyx_eq_sp}\n  共{len(tpandyx_eq_sp)}条')
