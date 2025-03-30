# coding=cp936
import csv
import numpy as np
from base import work_path, data_path
from odbAccess import openOdb

# ·��
odb_name = 'job-1.odb'
path = work_path + '/' + odb_name

# ��odb
odb = openOdb(path)
node = odb.rootAssembly.instances['REINBAR-1'].nodeSets['LEFT']

# Ӧ����Ӧ��
s_max = np.array([])
e_max = np.array([])

# ��ȡ����
for step in odb.steps.values():
    for frame in step.frames:
        s_out = frame.fieldOutputs['S']
        e_out = frame.fieldOutputs['E']

        s_max = np.append(s_max, s_out.getSubset(region=node).values[0].maxPrincipal)
        e_max = np.append(e_max, e_out.getSubset(region=node).values[0].maxPrincipal)

# ���� csv
csv_name = 'ReinBar_SMAX_EMAX.csv'
with open(data_path + '/' + csv_name, mode='w') as file:
    writer = csv.writer(file, lineterminator='\n')
    writer.writerow(['SMAX', 'EMAX'])
    writer.writerows(np.column_stack([s_max, e_max]))
