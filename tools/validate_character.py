import bpy, os, math
from mathutils import Vector
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=root+'/Assets/RedCrewmate/RedCrewmate.fbx')
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
assert len(meshes)==4 and len(rigs)==1
rig=rigs[0];assert len(rig.data.bones)==4
for ob in meshes:
 assert len(ob.data.uv_layers)>0
 assert all(all(math.isfinite(c) for c in v.co) for v in ob.data.vertices)
 assert all(abs(sum(g.weight for g in v.groups)-1)<.001 for v in ob.data.vertices)
 assert any(m.type=='ARMATURE' for m in ob.modifiers)
 print(ob.name,'vertices',len(ob.data.vertices),'triangles',sum(len(p.vertices)-2 for p in ob.data.polygons))
actions=list(bpy.data.actions);print('Actions',[(a.name,a.frame_range[:]) for a in actions]);assert any('Idle' in a.name for a in actions);assert any('Walk' in a.name for a in actions)
body=next(o for o in meshes if o.name=='Suit')
rig.animation_data.action=next(a for a in actions if 'Walk' in a.name)
bpy.context.scene.frame_set(1);deps=bpy.context.evaluated_depsgraph_get();before=[v.co.copy() for v in body.evaluated_get(deps).data.vertices]
bpy.context.scene.frame_set(7);deps=bpy.context.evaluated_depsgraph_get();after=[v.co.copy() for v in body.evaluated_get(deps).data.vertices]
assert max((a-b).length for a,b in zip(before,after))>.03
print('PASS: mesh, UVs, normalized skin weights, rig, two clips, animated deformation')
