# coding=cp936
"""
ABAQUS ��������� (CDP) �������˱���

* ���ݡ��������ṹ��ƹ淶��GB50010-2010 (2024���)
* ���û�����ǿ�ȵȼ���Χ C20~C80
"""
import numpy as np
from abaqus import *


def cal_ec(fcu_k):
    """
    ���㵯��ģ��
    :param fcu_k: �����忹ѹǿ�ȱ�׼ֵ��
    :return: ����ģ��
    """
    ec = 10 ** 5 / (2.2 + 34.7 / fcu_k)
    ec = round(ec, 3)
    return ec


def convert_fcu_k(fcu_k=30, delta_c=None):
    """
    fcu,k ����� fck, ftk

    :param fcu_k: �����忹ѹǿ�ȱ�׼ֵ��ǿ�ȵȼ�����ֵ�� (N/mm^2)��
    :param delta_c:  ����ϵ�� ��c, ���Ϊ None, �򰴹淶��ʽ���㡣
    """

    # �����Բ�ֵ���� ��1, ��2
    if fcu_k <= 50:
        alpha1 = 0.76
    else:
        alpha1 = np.interp(fcu_k, [50, 80], [0.76, 0.82])

    if fcu_k <= 40:
        alpha2 = 1
    else:
        alpha2 = np.interp(fcu_k, [40, 80], [1, 0.87])

    # �������ϵ��
    if delta_c is None:
        if fcu_k <= 20:
            delta_c = 0.18
        elif fcu_k <= 25:
            delta_c = 0.16
        elif fcu_k <= 30:
            delta_c = 0.14
        elif fcu_k <= 35:
            delta_c = 0.13
        elif fcu_k <= 45:
            delta_c = 0.12
        elif fcu_k <= 55:
            delta_c = 0.11
        else:
            delta_c = 0.10

    # ����
    fck = 0.88 * alpha1 * alpha2 * fcu_k
    ftk = 0.88 * 0.395 * fcu_k ** 0.55 * (1 - 1.645 * delta_c) ** 0.45 * alpha2

    return fck, ftk


class Concrete:
    def __init__(self,
                 name='C30',
                 fcr=20.1,
                 ftr=2.01,
                 er=30000,
                 density=2.4e-09,
                 poisson=0.2,
                 cdp_plasticity=(30.0, 0.1, 1.16, 0.6667, 0.005)):
        """
        ��������
        :param name: ����
        :param fcr: ���Όѹǿ�ȴ���ֵ����ȡ fc��fck��fcm (N/mm^2)
        :param ftr: ���Ό��ǿ�ȴ���ֵ����ȡ ft��ftk��ftm (N/mm^2)
        :param er:  Ec ����ģ�� (N/mm^2)
        :param poisson: ���ɱȣ���ȡ 0.2
        :param density: �� �ܶȣ�һ�� 2.2e-09~2.4e-09 (tone/mm^3)
        :param cdp_plasticity: CDP ���Բ���
        """

        self.name = name
        self.fcr = fcr
        self.ftr = ftr
        self.er = er
        self.density = density
        self.poisson = poisson
        self.cdp_plasticity = cdp_plasticity

    def compress(self):
        """
        �����������������ģ����ѹ����
        """
        x = np.concatenate([
            np.arange(0.3, 1, 0.1),
            np.arange(1, 4, 0.2),
            np.arange(4, 14, 0.5),
            np.arange(14, 50, 5)
        ])

        fcr = self.fcr
        er = self.er

        x0 = x[x <= 1]
        x1 = x[x > 1]

        # ��ֵѹӦ��
        strain_peek = (700 + 172 * np.sqrt(fcr)) * 1e-6

        # ��ѹӦ��Ӧ�������½��β���
        alpha = 0.157 * fcr ** 0.785 - 0.905

        # ��ѹӦ�������Բ���
        n = er * strain_peek / (er * strain_peek - fcr)

        # ��ѹ�������
        rho = fcr / (er * strain_peek)

        # ��ѹ�����ݻ�����
        dc_arg = np.append(
            1 - rho * n / (n - 1 + x0 ** n),
            1 - rho / (alpha * (x1 - 1) ** 2 + x1)
        )

        # ����Ӧ����Ӧ��
        strain_nominal = x * strain_peek
        stress_nominal = (1 - dc_arg) * er * strain_nominal

        # ��ѹ��������
        d = 1 - np.sqrt(stress_nominal / (er * strain_nominal))

        # ��ʵӦ����Ӧ��
        stress_true = stress_nominal * (1 + strain_nominal)
        strain_true = np.log(1 + strain_nominal)

        # �ǵ���Ӧ��
        strain_in = strain_true - (stress_true / er)

        return d, stress_true, strain_in

    def tensile(self):
        """
        �����������������ģ����������
        """
        x = np.concatenate([
            np.arange(1, 4, 0.2),
            np.arange(4, 14, 0.5),
            np.arange(14, 50, 5)
        ])

        ftr = self.ftr
        er = self.er
        x0 = x[x <= 1]
        x1 = x[x > 1]

        # ��ֵ��Ӧ��
        strain_peek = 65 * ftr ** 0.54 * 1e-6

        # ����Ӧ��Ӧ�������½��β���
        alpha = 0.312 * ftr ** 2

        # �����������
        rho = ftr / (er * strain_peek)

        # ���������ݻ�����
        dt_arg = np.append(
            1 - rho * (1.2 - 0.2 * x0 ** 5),
            1 - rho / (alpha * (x1 - 1) ** 1.7 + x1)
        )

        # ����Ӧ����Ӧ��
        strain_nominal = x * strain_peek
        stress_nominal = (1 - dt_arg) * er * strain_nominal

        # ������������
        d = 1 - np.sqrt(stress_nominal / (er * strain_nominal))

        # ��ʵӦ����Ӧ��
        stress_true = stress_nominal * (1 + strain_nominal)
        strain_true = np.log(1 + strain_nominal)

        # ����Ӧ��
        strain_in = strain_true - (stress_true / er)

        return d, stress_true, strain_in


class ConcreteAb(Concrete):
    def __init__(self,
                 model_name,
                 name='C30',
                 fcr=20.1,
                 ftr=2.01,
                 er=30000,
                 density=2.4e-09,
                 poisson=0.2,
                 cdp_plasticity=(30.0, 0.1, 1.16, 0.6667, 0.005)):
        """
        ABAQUS ��������
        :param model_name: ģ����
        :param name: ����
        :param fcr: ���Όѹǿ�ȴ���ֵ����ȡ fc��fck��fcm (N/mm^2)
        :param ftr: ���Ό��ǿ�ȴ���ֵ����ȡ ft��ftk��ftm (N/mm^2)
        :param er:  Ec ����ģ�� (N/mm^2)
        :param poisson: ���ɱȣ���ȡ 0.2
        :param density: �� �ܶȣ�һ�� 2.2e-09~2.4e-09 (tone/mm^3)
        :param cdp_plasticity: CDP ���Բ���
        """
        Concrete.__init__(self, name, fcr, ftr, er, density, poisson, cdp_plasticity)
        self.model = mdb.models[model_name]

    def create(self):
        """
        �������������ϣ�������CDP�������ˣ��������������������Բ������� Abaqus
        :return:
        """
        name = self.name
        er = self.er
        model = self.model

        # ���
        if name in model.materials.keys():
            return model.materials[name]

        # ����
        dc_in, stress_c_in, strain_c_in = self.compress()
        dt_in, stress_t_in, strain_t_in = self.tensile()

        # ����
        dt_in = np.round(dt_in, 5)
        dc_in = np.round(dc_in, 5)
        stress_t_in = np.round(stress_t_in, 6)
        stress_c_in = np.round(stress_c_in, 6)
        strain_t_in = np.round(strain_t_in, 6)
        strain_c_in = np.round(strain_c_in, 6)
        dc_in[0] = 0
        dt_in[0] = 0
        strain_t_in[0] = 0
        strain_c_in[0] = 0

        # ����
        material = model.Material(name=name)
        material.Density(table=((self.density,),))
        material.Elastic(table=((er, self.poisson),))
        cdp = material.ConcreteDamagedPlasticity(table=(self.cdp_plasticity,))
        cdp.ConcreteCompressionHardening(table=np.column_stack([stress_c_in, strain_c_in]))
        cdp.ConcreteTensionStiffening(table=np.column_stack([stress_t_in, strain_t_in]))
        cdp.ConcreteCompressionDamage(table=np.column_stack([dc_in, strain_c_in]))
        cdp.ConcreteTensionDamage(table=np.column_stack([dt_in, strain_t_in]))

        print('Python: �������� ' + name)
        return material
