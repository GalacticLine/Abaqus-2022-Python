# coding=cp936
from abaqus import *
from abaqusConstants import *


class Cube:
    def __init__(self,
                 model_name,
                 name='Cube',
                 length=100.0,
                 width=100.0,
                 height=100.0,
                 section_name='',
                 need_surf_top=False,
                 need_surf_bottom=False,
                 need_repoint=False):
        """
        3ά-�ɱ��� ����ʵ�岿��
        :param model_name: ģ��

        :param name: ������
        :param length: ��
        :param width: ��
        :param height: ��
        :param section_name: ������
        :param need_surf_top: �Ƿ����ö��� "Top"
        :param need_surf_bottom: �Ƿ����õ��� "Bottom"
        :param need_repoint: �Ƿ��ڵ������òο���
        """

        def create():
            # ���
            model = mdb.models[model_name]
            if name in model.parts.keys():
                return model.parts[name]

            # ����
            x = length / 2
            y = width / 2
            sketch = model.ConstrainedSketch(name='__profile__', sheetSize=1.2 * max(length, width))
            sketch.rectangle(point1=(-x, -y), point2=(x, y))

            # ����
            part = model.Part(name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
            part.BaseSolidExtrude(sketch=sketch, depth=height)
            del model.sketches[sketch.name]

            # ����ָ��
            if section_name in model.sections.keys():
                region = part.Set(name='All', cells=part.cells)
                part.SectionAssignment(region=region, sectionName=section_name)
                self.set_all = region

            # ��������
            if need_surf_top:
                self.surf_top = part.Surface(name='Top', side1Faces=part.faces.getByBoundingBox(zMin=height))

            if need_surf_bottom:
                self.surf_bottom = part.Surface(name='Bottom', side1Faces=part.faces.getByBoundingBox(zMax=0))

            if need_repoint:
                self.rp0 = part.ReferencePoint(point=(0.0, 0.0, 0.0))

            print('Python: �������� ' + name)
            return part

        self.part = create()


class SimplyBeam(Cube):
    def __init__(self,
                 model_name,
                 name='Beam',
                 length=2000.0,
                 width=200.0,
                 height=300.0,
                 section_name='',
                 need_surf_top=False,
                 need_surf_bottom=False,
                 need_repoint=False,
                 pad_width=0.0,
                 load_mode=0):
        """
        3ά-�ɱ��� ��֧��ʵ�岿��
        :param name: ����
        :param length: ��
        :param width: ��
        :param height: ��
        :param section_name: ������
        :param need_surf_top: �Ƿ����ö��� "Top"
        :param need_surf_bottom: �Ƿ����õ��� "Bottom"
        :param need_repoint: �Ƿ��ڵ������òο���
        :param pad_width: ����ȣ�Ĭ�� 0.0 �����õ�飬�����õ��󣬴������� "ToPads"
        :param load_mode: ������ģʽ�ָ�ģ�ͣ�������������ر��� "ToLoad"��( 0 �������أ�1 ������м��أ�2 ���ֵ���� )
        """

        def create():
            # ���
            model = mdb.models[model_name]
            if name in model.parts.keys():
                return model.parts[name]

            Cube.__init__(self, model_name, name, length, width, height, section_name, need_surf_top, need_surf_bottom,
                          need_repoint)
            part = self.part

            y = width / 2

            # ���зָ�
            dp0 = part.DatumPointByCoordinate(coords=(0, y, height))
            part.PartitionCellByPlanePointNormal(point=part.datums[dp0.id],
                                                 normal=part.edges.findAt((1e-2, y, 0)),
                                                 cells=part.cells)
            # ���е�
            part.PartitionEdgeByParam(edges=part.edges.findAt((0, 1e-2, 0)), parameter=0.5)
            self.mid_point = part.Set(vertices=
                                      part.vertices.getByBoundingBox(xMin=0, yMin=0, zMin=0, zMax=0, xMax=0, yMax=0),
                                      name='MidPoint')

            # ֧���ָ�
            if pad_width != 0:
                x = length / 2 - pad_width
                dp0 = part.DatumPointByCoordinate(coords=(x, y, height))
                dp1 = part.DatumPointByCoordinate(coords=(-x, y, height))

                part.PartitionCellByPlanePointNormal(point=part.datums[dp0.id],
                                                     normal=part.edges.findAt((1e-2, y, 0)),
                                                     cells=part.cells)
                part.PartitionCellByPlanePointNormal(point=part.datums[dp1.id],
                                                     normal=part.edges.findAt((1e-2, y, 0)),
                                                     cells=part.cells)

                part.Surface(side1Faces=
                             part.faces.getByBoundingBox(xMin=x, zMax=0) +
                             part.faces.getByBoundingBox(xMax=-x, zMax=0), name='ToPads')

            # ��������
            surf_load_name = 'ToLoad'
            if load_mode == 0:
                part.Surface(side1Faces=part.faces.getByBoundingBox(zMin=height), name=surf_load_name)

            # ���е������
            if load_mode == 1:
                x = pad_width / 2

                dp0 = part.DatumPointByCoordinate(coords=(x, y, height))
                dp1 = part.DatumPointByCoordinate(coords=(-x, y, height))

                part.PartitionCellByPlanePointNormal(point=part.datums[dp0.id],
                                                     normal=part.edges.findAt((1e-2, y, 0)),
                                                     cells=part.cells)
                part.PartitionCellByPlanePointNormal(point=part.datums[dp1.id],
                                                     normal=part.edges.findAt((1e-2, y, 0)),
                                                     cells=part.cells)
                part.Surface(side1Faces=
                             part.faces.getByBoundingBox(xMax=x, xMin=-x, zMin=height),
                             name=surf_load_name)

            # ���ֵ����
            if load_mode == 2:
                x0 = length / 6 + pad_width / 2
                x1 = length / 6 - pad_width / 2

                dp0 = part.DatumPointByCoordinate(coords=(x0, y, height))
                dp1 = part.DatumPointByCoordinate(coords=(x1, y, height))
                dp2 = part.DatumPointByCoordinate(coords=(-x1, y, height))
                dp3 = part.DatumPointByCoordinate(coords=(-x0, y, height))

                part.PartitionCellByPlanePointNormal(point=part.datums[dp0.id],
                                                     normal=part.edges.findAt((1e-2, y, 0)),
                                                     cells=part.cells)
                part.PartitionCellByPlanePointNormal(point=part.datums[dp1.id],
                                                     normal=part.edges.findAt((1e-2, y, 0)),
                                                     cells=part.cells)
                part.PartitionCellByPlanePointNormal(point=part.datums[dp2.id],
                                                     normal=part.edges.findAt((1e-2, y, 0)),
                                                     cells=part.cells)
                part.PartitionCellByPlanePointNormal(point=part.datums[dp3.id],
                                                     normal=part.edges.findAt((1e-2, y, 0)),
                                                     cells=part.cells)

                part.Surface(side1Faces=
                             part.faces.getByBoundingBox(xMax=x0, xMin=x1, zMin=height) +
                             part.faces.getByBoundingBox(xMax=-x1, xMin=-x0, zMin=height),
                             name=surf_load_name)
            return part

        self.part = create()
