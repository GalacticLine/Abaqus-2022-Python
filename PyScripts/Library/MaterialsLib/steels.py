# coding=cp936
"""
Abaqus ����ֲı���

* ����˫����ģ��
"""
from abaqus import *


class SteelArgs:
    RigidSteel = [7.85e-09, 2.1e5, 0.3, None, None]
    HRB335 = [7.85e-09, 2e5, 0.3, 335, 455]
    HRB400 = [7.85e-09, 2e5, 0.3, 400, 540]
    HRB500 = [7.85e-09, 2e5, 0.3, 500, 630]
    HPB300 = [7.85e-09, 2.1e5, 0.3, 300, 420]
    Bolt64 = [7.85e-09, 2.06e5, 0.3, 640, 800]
    Q235 = [7.85e-09, 2e5, 0.3, 235, 370]
    Q345 = [7.85e-09, 2e5, 0.3, 345, 470]
    Q355 = [7.85e-09, 2e5, 0.3, 355, 470]


class Steel:
    def __init__(self,
                 model_name,
                 name='HRB400',
                 rho=7.85e-09,
                 es=2e5,
                 poisson=0.2,
                 yie=400,
                 limit=540):
        """
        �ֽ���
        :param model_name: ģ����
        :param name: ������
        :param rho: �ܶ�
        :param es: ����ģ��
        :param poisson: ���ɱ�
        :param yie: ����Ӧ��
        :param limit: ����Ӧ��
        """
        self.model = mdb.models[model_name]
        self.name = name
        self.rho = rho
        self.es = es
        self.poisson = poisson
        self.yie = yie
        self.limit = limit

    def create(self):
        """
        �����ֲģ�����abaqus
        :return:
        """
        name = self.name
        rho = self.rho
        es = self.es
        poisson = self.poisson
        yie = self.yie
        limit = self.limit
        model = self.model

        # ���
        if name in model.materials.keys():
            return model.materials[name]

        # ����
        material = model.Material(name)
        material.Density(((rho,),))
        material.Elastic(((es, poisson),))
        if yie and limit is not None:
            material.Plastic(((yie, 0.0), (limit, 0.1)))

        print('Python: �������� ' + name)
        return material
