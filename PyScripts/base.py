# coding=cp936
import os
import inspect

# ��ȡ���������ߵ��ļ�·��
frame = inspect.currentframe()
while frame.f_back is not None:
    frame = frame.f_back
call_path = os.path.dirname(os.path.abspath(frame.f_code.co_filename))
del frame

# ����·��
work_path = os.path.join(call_path, 'Result')
data_path = os.path.join(work_path, 'Data')
img_path = os.path.join(work_path, 'Img')

# ����Ŀ¼
if not os.path.exists(work_path):
    os.makedirs(work_path)
if not os.path.exists(data_path):
    os.makedirs(data_path)
if not os.path.exists(img_path):
    os.makedirs(img_path)

os.chdir(work_path)
print("Python: ����Ŀ¼ " + work_path)
