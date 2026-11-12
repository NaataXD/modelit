import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=ROOT+'/Assets/RedCrewmate'
os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,color,rough=.5,metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
 return m
red=mat('Suit_Red',(0.65,.006,.015),.55)
black=mat('Visor_Rubber',(.009,.012,.016),.7)
blue=mat('Visor_Blue',(.12,.49,.75),.25,.12)
def signed(v,p): return math.copysign(abs(v)**p,v)
def shape(name,center,scale,power,material,segments=64,rings=32):
 verts=[]; faces=[]
 # Superellipsoid with single pole vertices avoids degenerate triangles.
 verts.append((center[0],center[1],center[2]-scale[2]))
 for j in range(1,rings):
  lat=-math.pi/2+math.pi*j/rings
  for i in range(segments):
   lon=2*math.pi*i/segments
   verts.append((center[0]+scale[0]*signed(math.cos(lat),power)*signed(math.cos(lon),power),center[1]+scale[1]*signed(math.cos(lat),power)*signed(math.sin(lon),power),center[2]+scale[2]*signed(math.sin(lat),power)))
 top=len(verts); verts.append((center[0],center[1],center[2]+scale[2]))
 for i in range(segments): faces.append((0,1+(i+1)%segments,1+i))
 for j in range(rings-2):
  for i in range(segments):
   a=1+j*segments+i; b=1+j*segments+(i+1)%segments
   faces.append((a,b,b+segments,a+segments))
 for i in range(segments): faces.append((top,1+(rings-2)*segments+i,1+(rings-2)*segments+(i+1)%segments))
 mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
 ob=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(ob); ob.data.materials.append(material)
 for f in mesh.polygons:f.use_smooth=True
 return ob
# Profile rings give the suit a domed head and straight, soft sidewalls.
def suit_mesh():
 profile=[(.43,.32,.26),(.49,.43,.315),(.60,.49,.35),(.8,.505,.36),(1.1,.51,.365),(1.4,.505,.36),(1.57,.48,.345),(1.72,.425,.305),(1.85,.32,.235),(1.94,.18,.14),(1.98,.065,.055)]
 verts=[(0,0,.43)];faces=[];n=64
 for z,rx,ry in profile:
  for i in range(n):
   a=2*math.pi*i/n;verts.append((rx*signed(math.cos(a),.86),ry*signed(math.sin(a),.86),z))
 for i in range(n):faces.append((0,1+(i+1)%n,1+i))
 for j in range(len(profile)-1):
  for i in range(n):
   a=1+j*n+i;b=1+j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
 top=len(verts);verts.append((0,0,1.99))
 for i in range(n):faces.append((top,1+(len(profile)-1)*n+i,1+(len(profile)-1)*n+(i+1)%n))
 me=bpy.data.meshes.new('Suit_Profile');me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new('Suit',me);bpy.context.collection.objects.link(ob);ob.data.materials.append(red);return ob
body=suit_mesh()
legs=[shape('Leg_L',(-.27,0,.295),(.235,.315,.295),.43,red),shape('Leg_R',(.27,0,.295),(.235,.315,.295),.43,red)]
bpy.ops.object.select_all(action='DESELECT')
for o in [body]+legs:o.select_set(True)
bpy.context.view_layer.objects.active=body; bpy.ops.object.join()
rem=body.modifiers.new('Seamless suit','REMESH');rem.mode='VOXEL';rem.voxel_size=.013;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
sm=body.modifiers.new('Soft silhouette','SMOOTH');sm.factor=1.0;sm.iterations=9;bpy.ops.object.modifier_apply(modifier=sm.name)
dec=body.modifiers.new('Game mesh','DECIMATE');dec.ratio=.14;bpy.ops.object.modifier_apply(modifier=dec.name)
# Front faces -Y; backpack is on +Y. Height is two metres.
pack=shape('Backpack',(0,.405,1.045),(.375,.235,.50),.48,red)
rim=shape('Visor_Rim',(0,-.315,1.48),(.457,.15,.302),.66,black)
visor=shape('Visor',(0,-.418,1.495),(.412,.14,.242),.70,blue)
parts=[body,pack,rim,visor]
for o in parts:
 bpy.context.view_layer.objects.active=o
 o.select_set(True)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 # UVs for future texturing.
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
# Bake restrained fabric variation into a portable Unity base-color map.
nodes=red.node_tree.nodes;links=red.node_tree.links;bs=nodes.get('Principled BSDF')
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=48;noise.inputs['Detail'].default_value=3
ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(.43,.003,.008,1);ramp.color_ramp.elements[1].position=.85;ramp.color_ramp.elements[1].color=(.70,.009,.018,1)
links.new(noise.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs[0],bs.inputs['Base Color'])
bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.009;links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
# Shared texture uses separate UV regions for suit and backpack.
for ob,offset in [(body,0),(pack,.5)]:
 for uv in ob.data.uv_layers.active.data:uv.uv.x=uv.uv.x*.49+offset
image=bpy.data.images.new('Suit_BaseColor',width=1024,height=1024)
tex=nodes.new('ShaderNodeTexImage');tex.image=image;nodes.active=tex
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);pack.select_set(True);bpy.context.view_layer.objects.active=body
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=False
scene.render.bake.use_pass_direct=False;scene.render.bake.use_pass_indirect=False;scene.render.bake.use_pass_color=True;scene.render.bake.margin=12
bpy.ops.object.bake(type='DIFFUSE');image.filepath_raw=OUT+'/Suit_BaseColor.png';image.file_format='PNG';image.save();image.pack();links.new(tex.outputs['Color'],bs.inputs['Base Color'])
# Four-bone Generic rig with continuous suit weights.
arm=bpy.data.armatures.new('CrewmateRig');root=bpy.data.objects.new('RedCrewmate',arm);bpy.context.collection.objects.link(root)
bpy.context.view_layer.objects.active=root;root.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for name,head,tail,parent in [('Root',(0,0,0),(0,0,.25),None),('Body',(0,0,.65),(0,0,1.7),'Root'),('Leg_L',(-.27,0,.52),(-.27,0,.10),'Root'),('Leg_R',(.27,0,.52),(.27,0,.10),'Root')]:
 bone=arm.edit_bones.new(name);bone.head=head;bone.tail=tail
 if parent:bone.parent=arm.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT')
for ob in parts:
 groups={name:ob.vertex_groups.new(name=name) for name in ['Body','Leg_L','Leg_R']}
 for v in ob.data.vertices:
  if ob!=body:groups['Body'].add([v.index],1,'REPLACE');continue
  t=max(0,min(1,(.76-v.co.z)/.36));t=t*t*(3-2*t)
  groups['Body'].add([v.index],1-t,'REPLACE');groups['Leg_L' if v.co.x<0 else 'Leg_R'].add([v.index],t,'REPLACE')
 mod=ob.modifiers.new('Crewmate skin','ARMATURE');mod.object=root
# In-place walk cycle, suitable for a Generic Animator.
root.animation_data_create()
for name,end in [('Idle',60),('Walk',24)]:
 action=bpy.data.actions.new(name);action.use_fake_user=True;root.animation_data.action=action
 for f in range(1,end+2,3):
  phase=(f-1)/end*2*math.pi
  for bone_name,sign in [('Leg_L',1),('Leg_R',-1)]:
   pb=root.pose.bones[bone_name];pb.rotation_mode='XYZ';pb.rotation_euler=(sign*math.sin(phase)*(.42 if name=='Walk' else 0),0,0);pb.keyframe_insert('rotation_euler',frame=f,group=bone_name)
  pb=root.pose.bones['Body'];pb.location=(0,0,math.sin(phase*(2 if name=='Walk' else 1))*(.022 if name=='Walk' else .008));pb.keyframe_insert('location',frame=f,group='Body')
root.animation_data.action=None
for pb in root.pose.bones:pb.rotation_euler=(0,0,0);pb.location=(0,0,0)
bpy.context.scene.render.fps=30
bpy.context.scene.frame_set(1)

for o in parts:o.parent=root
bpy.ops.object.select_all(action='DESELECT')
for o in parts+[root]:o.select_set(True)
bpy.context.view_layer.objects.active=body
bpy.ops.export_scene.fbx(filepath=OUT+'/RedCrewmate.fbx',use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,add_leaf_bones=False,bake_anim=True,bake_anim_use_nla_strips=False,bake_anim_use_all_actions=True,bake_anim_simplify_factor=0)
os.makedirs(ROOT+'/Sources',exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/Sources/RedCrewmate.blend')
# Product preview, excluded from exported model.
floor=mat('Preview floor',(.15,.18,.19),.8)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.025));bpy.context.object.data.materials.append(floor)
world=bpy.context.scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.3,.34,.36,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for loc,power,size in [((-3,-4,6),500,4),((4,-1,3),250,3),((0,4,4),400,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);bpy.context.object.data.energy=power;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=size;aim(bpy.context.object,(0,0,1))
bpy.ops.object.camera_add(location=(-3.1,-5,2.55));cam=bpy.context.object;aim(cam,(0,0,1));cam.data.type='ORTHO';cam.data.ortho_scale=2.7
sc=bpy.context.scene;sc.camera=cam;sc.render.engine='CYCLES';sc.cycles.samples=128;sc.cycles.use_denoising=False;sc.render.resolution_x=1000;sc.render.resolution_y=1100;sc.render.resolution_percentage=100
sc.render.filepath=ROOT+'/Preview.png';bpy.ops.render.render(write_still=True)
cam.location=(3.4,5,2.6);aim(cam,(0,0,1));sc.render.filepath=ROOT+'/Preview_Back.png';bpy.ops.render.render(write_still=True)
print('MODEL_REPORT',{'mesh_parts':len(parts),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in parts),'height_metres':2.0})
