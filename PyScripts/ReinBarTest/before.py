# coding=cp936
import math
from abaqus import *
from abaqusConstants import *
from caeModules import *

# ������Ŀģ�飨����ͳһ·����
from base import *

# ģ�� SI(mm)
model = mdb.models['Model-1']
assem = model.rootAssembly

# �ֽ
length = 100
# �ֽ�ֱ��
d = 8
# �ֲ���
material_name = 'HRB400'
# �ܶ�
rho = 7.85e-09
# ����ģ��
e = 2e5
poisson = 0.3
# ����Ӧ��
yie = 400.0
# ����Ӧ��
limit = 540
# ��������С
load_force = 30000.0
# �����С
mesh_size = 5.0

x = length / 2

# ��ͼ
skh = model.ConstrainedSketch(name='__profile__', sheetSize=1.2 * length)
skh.Line(point1=(-x, 0.0), point2=(x, 0.0))

# ��������
part = model.Part(name='ReinBar', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseWire(sketch=skh)
del model.sketches[skh.name]

# ��������
hrb400 = model.Material(name=material_name)
hrb400.Density(table=((rho,),))
hrb400.Elastic(table=((e, poisson),))
hrb400.Plastic(scaleStress=None, table=((yie, 0.0), (limit, 0.1)))

# ��������
section_name = 'TrD%d' % d + material_name
model.TrussSection(name=section_name, material=hrb400.name, area=(d / 2) ** 2 * math.pi)
set_all = part.Set(edges=part.edges, name='All')
part.SectionAssignment(region=set_all, sectionName=section_name, offsetType=MIDDLE_SURFACE, )

# װ��
instance = assem.Instance(name=part.name + '-1', part=part, dependent=ON)

# ������
step1 = model.StaticStep(name='Step-1', previous='Initial', initialInc=0.01, timePeriod=2, maxInc=2)

# ��
set_right = part.Set(vertices=part.vertices.getByBoundingBox(xMax=-x), name='Right')
model.DisplacementBC(name='BC-1',
                     createStepName=step1.name,
                     region=instance.sets['Right'],
                     u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET)

# ����
set_left = part.Set(vertices=part.vertices.getByBoundingBox(xMin=x), name='Left')
model.ConcentratedForce(name='Load-CF',
                        createStepName=step1.name,
                        region=instance.sets['Left'],
                        cf1=load_force)

# �����
model.FieldOutputRequest(name='F-Output-1',
                         createStepName=step1.name, variables=('S', 'E'), timeInterval=0.05,
                         position=NODES)

# ��������
part.seedPart(size=mesh_size, deviationFactor=0.1, minSizeFactor=0.1)
t3d2 = mesh.ElemType(elemCode=T3D2, elemLibrary=STANDARD)
part.setElementType(regions=regionToolset.Region(edges=part.edges), elemTypes=(t3d2,))
part.generateMesh()

# �ύ��ҵ
job = mdb.Job(name='Job-1', model=model)
job.submit(consistencyChecking=OFF)

# ����
mdb.saveAs('ReinBarTest.cae')
mdb.close()
