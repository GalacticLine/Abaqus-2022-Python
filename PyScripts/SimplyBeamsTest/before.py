# coding=cp936
import math
import regionToolset
from abaqus import *
from abaqusConstants import *
from caeModules import mesh
from Library import *
from base import *


# ģ��
def main(model_name='Model-SimplyBeam',
         # ��
         beam_name='Beam',
         beam_length=5000.0,
         beam_width=300.0,
         beam_height=500.0,
         # ������
         ax=25.0,
         ay=25.0,
         az=25.0,
         # ���
         pad_name='Pad',
         pad_width=200.0,
         pad_height=50.0,
         # �ֽ�
         rm_name='ReinMesh',
         # ������
         r0_num=2,
         r0_d=12.0,
         r0_material='HRB400',
         r0_args=SteelArgs.HRB400,
         # �ײ�������
         r1_num=3,
         r1_d=18.0,
         r1_material='HRB400',
         r1_args=SteelArgs.HRB400,
         # ����
         r2_d=8.0,
         r2_spacing=200.0,
         r2_material='HPB300',
         r2_args=SteelArgs.HPB300,
         # ����������
         concrete_name='C30',
         fcr=20.1,
         ftr=2.01,
         # �ֲ�
         rigid_steel_name='RigidSteel',
         rigid_steel_args=SteelArgs.RigidSteel,
         # ����
         load_mode=2,
         load_force=70000.0,
         # ����
         beam_mesh_size=50,
         pad_mesh_size=25,
         rein_mesh_size=50,
         # ��ҵ
         num_cpu=4
         ):
    """
     ��֧��ģ�ͽ�ģ������

    :param model_name: ģ����

    :param beam_name: ����
    :param beam_length: ����
    :param beam_width: ����
    :param beam_height: ����

    :param ax: x ���򱣻����
    :param ay: y ���򱣻����
    :param az: z ���򱣻����

    :param pad_name: �����
    :param pad_width: ����
    :param pad_height: ����

    :param rm_name: �ֽ�����
    :param r0_num: ��������
    :param r0_d: ������ֱ��
    :param r0_material: ��������
    :param r0_args: �����������
    :param r1_num: ��������
    :param r1_d: ������ֱ��
    :param r1_material: �ײ��ݽ���
    :param r1_args: �����������
    :param r2_d: ����ֱ��
    :param r2_spacing: ������
    :param r2_material: ������
    :param r2_args: ���������

    :param concrete_name: ������������
    :param fcr: ��ѹǿ�ȴ���ֵ
    :param ftr: ����ǿ�ȴ���ֵ

    :param rigid_steel_name: ���Ըְ���
    :param rigid_steel_args: ���Ըְ屾������

    :param load_mode: ����ģʽ ( 0 �������أ�1 ������м��أ�2 ���ֵ���� )
    :param load_force: ��������С kN

    :param beam_mesh_size: ��������
    :param pad_mesh_size: ���������
    :param rein_mesh_size: �ֽ���������

    :param num_cpu: ��ҵcpu�߳���
    :return:
    """
    # region ģ��
    if model_name in mdb.models.keys():
        model = mdb.models[model_name]
    else:
        model = mdb.Model(name=model_name)

    a = model.rootAssembly
    # endregion

    # region ��������
    ConcreteAb(model_name, concrete_name, fcr, ftr).create()
    Steel(model_name, r0_material, *r0_args).create()
    Steel(model_name, r1_material, *r1_args).create()
    Steel(model_name, r2_material, *r2_args).create()
    Steel(model_name, rigid_steel_name, *rigid_steel_args).create()
    # endregion

    # ��������
    def cal_area(d):
        return (d / 2) ** 2 * math.pi

    class Sec:
        r0 = model.TrussSection(name='TrD%d' % r0_d + r0_material,
                                material=r0_material,
                                area=cal_area(r0_d)
                                ).name

        r1 = model.TrussSection(name='TrD%d' % r1_d + r1_material,
                                material=r1_material,
                                area=cal_area(r1_d)
                                ).name

        r2 = model.TrussSection(name='TrD%d' % r2_d + r2_material,
                                material=r2_material,
                                area=cal_area(r2_d)
                                ).name

        concrete = model.HomogeneousSolidSection(name='Hm' + concrete_name,
                                                 material=concrete_name,
                                                 thickness=None
                                                 ).name

        rigid = model.HomogeneousSolidSection(name='Hm' + rigid_steel_name,
                                              material=rigid_steel_name,
                                              thickness=None
                                              ).name

    # ��������
    class P:
        # �ֽ���
        rm = Lines.create_beam_mesh(model_name,
                                    name=rm_name,
                                    length=beam_length - ax * 2,
                                    width=beam_width - ay * 2,
                                    height=beam_height - az * 2,
                                    num_top=r0_num,
                                    num_bottom=r1_num,
                                    spacing_stirrup=r2_spacing,
                                    section_name_top=Sec.r0,
                                    section_name_bottom=Sec.r1,
                                    section_name_stirrup=Sec.r2)

        # ��
        beam = SimplyBeam(model_name,
                          name=beam_name,
                          length=beam_length,
                          width=beam_width,
                          height=beam_height,
                          section_name=Sec.concrete,
                          pad_width=pad_width,
                          load_mode=load_mode).part

        # ���
        pad = Cube(model_name,
                   name=pad_name,
                   length=pad_width,
                   width=beam_width,
                   height=pad_height,
                   section_name=Sec.rigid,
                   need_surf_top=True,
                   need_surf_bottom=True,
                   need_repoint=True).part

    # region ����ʵ��
    beam = a.Instance(name=P.beam.name + '1', part=P.beam, dependent=ON)
    rm = a.Instance(name=P.rm.name + '1', part=P.rm, dependent=ON)
    pad0 = a.Instance(name=P.pad.name + 'L', part=P.pad, dependent=ON)
    pad1 = a.Instance(name=P.pad.name + 'R', part=P.pad, dependent=ON)

    if load_mode == 1:
        pad_t0 = a.Instance(name=P.pad.name + 'T', part=P.pad, dependent=ON)
        pad_t1 = None
    elif load_mode == 2:
        pad_t0 = a.Instance(name=P.pad.name + 'TL', part=P.pad, dependent=ON)
        pad_t1 = a.Instance(name=P.pad.name + 'TR', part=P.pad, dependent=ON)
    else:
        pad_t0 = None
        pad_t1 = None
    # endregion

    # region ʵ��λ�ñ任
    rm.translate(vector=(0, 0, az))
    pad0.translate(vector=(beam_length / 2 - pad_width / 2, 0, -pad_height))
    pad1.translate(vector=(-beam_length / 2 + pad_width / 2, 0, -pad_height))

    y_rotate180 = ((0, 0, 0), (0, 1, 0), 180)
    if load_mode == 1:
        pad_t0.rotateAboutAxis(*y_rotate180)
        pad_t0.translate(vector=(0, 0, beam_height + pad_height))
    if load_mode == 2:
        pad_t0.rotateAboutAxis(*y_rotate180)
        pad_t0.translate(vector=(beam_length / 6, 0, beam_height + pad_height))
        pad_t1.rotateAboutAxis(*y_rotate180)
        pad_t1.translate(vector=(-beam_length / 6, 0, beam_height + pad_height))

    # endregion

    # ������
    class St:
        rp0 = a.Set(name='RpL', referencePoints=(pad0.referencePoints.values()[0],))
        rp1 = a.Set(name='RpR', referencePoints=(pad1.referencePoints.values()[0],))
        if load_mode == 1:
            rp_t0 = a.Set(name='RpT', referencePoints=(pad_t0.referencePoints.values()[0],))
            rp_t1 = None
        elif load_mode == 2:
            rp_t0 = a.Set(name='RpTL', referencePoints=(pad_t0.referencePoints.values()[0],))
            rp_t1 = a.Set(name='RpTR', referencePoints=(pad_t1.referencePoints.values()[0],))
        else:
            rp_t0 = None
            rp_t1 = None

    # ��������
    class Sf:
        bc_pads = a.Surface(name='BCPads',
                            side1Faces=pad0.surfaces['Top'].faces + pad1.surfaces['Top'].faces)
        if load_mode == 1:
            load_pads = a.Surface(name='LoadPad',
                                  side1Faces=pad_t0.surfaces['Top'].faces)
        elif load_mode == 2:
            load_pads = a.Surface(name='LoadPads',
                                  side1Faces=pad_t0.surfaces['Top'].faces + pad_t1.surfaces['Top'].faces)
        else:
            load_pads = None

    # region ����������
    step0 = model.steps.keys()[0]
    step1 = model.StaticStep(name='Step-1',
                             previous=step0,
                             initialInc=0.01,
                             minInc=1e-6,
                             maxInc=0.2,
                             maxNumInc=10000,
                             timePeriod=0.2).name

    step2 = model.StaticStep(name='Step-2',
                             previous=step1,
                             initialInc=0.01,
                             minInc=1e-6,
                             maxInc=1,
                             maxNumInc=10000,
                             timePeriod=1).name
    # endregion

    # region ���ú���
    model.Gravity(name='Load-G',
                  createStepName=step1,
                  comp3=-9810)

    if load_mode == 0:
        model.Pressure(name='Load-P',
                       createStepName=step2,
                       region=beam.surfaces['ToLoad'],
                       distributionType=TOTAL_FORCE,
                       magnitude=load_force)
    if load_mode == 1:
        model.ConcentratedForce(name='Load-CF',
                                createStepName=step2,
                                region=St.rp_t0,
                                cf3=load_force)
    if load_mode == 2:
        model.ConcentratedForce(name='Load-CF',
                                createStepName=step2,
                                region=regionToolset.Region(referencePoints=
                                                            St.rp_t0.referencePoints + St.rp_t1.referencePoints),
                                cf3=load_force)
    # endregion

    # region �߽�����
    model.DisplacementBC(name='BC-R',
                         createStepName=step0,
                         region=St.rp1,
                         u1=UNSET, u2=SET, u3=SET,
                         ur1=SET, ur2=UNSET, ur3=SET)

    model.DisplacementBC(name='BC-L',
                         createStepName=step0,
                         region=St.rp0,
                         u1=SET, u2=SET, u3=SET,
                         ur1=SET, ur2=UNSET, ur3=SET)
    # endregion

    # region �������
    model.FieldOutputRequest(name='F-Output-1',
                             createStepName=step1,
                             variables=('E', 'S', 'U', 'DAMAGEC', 'DAMAGET'))

    model.HistoryOutputRequest(name='H-Output-1',
                               createStepName=step1,
                               variables=('U3',),
                               region=beam.sets['MidPoint'])

    model.HistoryOutputRequest(name='H-Output-2',
                               createStepName=step1,
                               variables=('RF3',),
                               region=St.rp0)

    model.HistoryOutputRequest(name='H-Output-3',
                               createStepName=step1,
                               variables=('RF3',),
                               region=St.rp1)
    # endregion

    # region ����Լ��
    model.Coupling(name='Cg-RpR',
                   controlPoint=St.rp1,
                   surface=pad1.surfaces['Bottom'],
                   influenceRadius=WHOLE_SURFACE,
                   couplingType=KINEMATIC)

    model.Coupling(name='Cg-RpL',
                   controlPoint=St.rp0,
                   surface=pad0.surfaces['Bottom'],
                   influenceRadius=WHOLE_SURFACE,
                   couplingType=KINEMATIC)

    if load_mode == 1:
        model.Coupling(name='Cg-RpT',
                       controlPoint=St.rp_t0,
                       surface=pad_t0.surfaces['Bottom'],
                       influenceRadius=WHOLE_SURFACE,
                       couplingType=KINEMATIC)

    if load_mode == 2:
        model.Coupling(name='Cg-RpTL',
                       controlPoint=St.rp_t0,
                       surface=pad_t0.surfaces['Bottom'],
                       influenceRadius=WHOLE_SURFACE,
                       couplingType=KINEMATIC)

        model.Coupling(name='Cg-RpTR',
                       controlPoint=St.rp_t1,
                       surface=pad_t1.surfaces['Bottom'],
                       influenceRadius=WHOLE_SURFACE,
                       couplingType=KINEMATIC)

    model.Tie(name="Tie-BeamPads",
              main=beam.surfaces['ToPads'],
              secondary=Sf.bc_pads,
              positionToleranceMethod=COMPUTED,
              adjust=ON,
              tieRotations=ON,
              thickness=ON)

    if load_mode != 0:
        model.Tie(name="Tie-BeamPadsT",
                  main=beam.surfaces['ToLoad'],
                  secondary=Sf.load_pads,
                  positionToleranceMethod=COMPUTED,
                  adjust=ON,
                  tieRotations=ON,
                  thickness=ON)

    model.EmbeddedRegion(name="Em-ReinMeshBeam",
                         embeddedRegion=regionToolset.Region(edges=rm.edges),
                         hostRegion=regionToolset.Region(cells=beam.cells),
                         weightFactorTolerance=1e-06,
                         absoluteTolerance=0.0,
                         fractionalTolerance=0.05,
                         toleranceMethod=BOTH)
    # endregion

    # region ��������
    t3d2 = mesh.ElemType(elemCode=T3D2, elemLibrary=STANDARD)

    if P.beam.getMeshStats().numMeshedRegions == 0:
        P.beam.seedPart(size=beam_mesh_size, deviationFactor=0.1, minSizeFactor=0.1)
        P.beam.generateMesh()

    if P.pad.getMeshStats().numMeshedRegions == 0:
        P.pad.seedPart(size=pad_mesh_size, deviationFactor=0.1, minSizeFactor=0.1)
        P.pad.generateMesh()

    if P.rm.getMeshStats().numMeshedRegions == 0:
        P.rm.seedEdgeByNumber(edges=P.rm.edges, number=1, constraint=FINER)
        P.rm.setElementType(regions=regionToolset.Region(edges=P.rm.edges), elemTypes=(t3d2,))
        P.rm.generateMesh()
    # endregion

    a.regenerate()

    # region �����ҵ
    if num_cpu > 1:
        job = mdb.Job(name='Job-' + model.name,
                      model=model.name,
                      numCpus=num_cpu,
                      numDomains=num_cpu,
                      multiprocessingMode=THREADS)
    else:
        job = mdb.Job(name='Job-' + model.name)
    job.submit(consistencyChecking=OFF)
    # endregion

    print('Python: ' + model_name + ' ������ɡ�')


if __name__ == '__main__':

    main('SimplyBeam0', load_mode=0, load_force=320*1e3)
    main('SimplyBeam1', load_mode=1, load_force=-180*1e3)
    main('SimplyBeam2', load_mode=2, load_force=-120*1e3)

    mdb.saveAs(pathName='SimplyBeamsTest.cae')
    mdb.close()
