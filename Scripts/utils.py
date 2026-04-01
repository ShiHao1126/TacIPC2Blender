import os
import bpy
import bmesh
import mathutils
import math

def import_obj(filepath):
    path_abs = os.path.abspath(filepath)
    assert os.path.isfile(path_abs), f"File not found: {path_abs}"
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.obj_import(filepath=path_abs)
    selected = list(bpy.context.selected_objects)
    assert len(selected) > 0, "No object imported"
    return selected[0]


def keep_top_surface_only(obj, sharpness=60.0):
    assert obj.type == 'MESH', "Object is not a mesh"
    mesh = obj.data
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(type='FACE')

    mw = obj.matrix_world
    bm = bmesh.from_edit_mesh(mesh)
    max_z = -float('inf')
    best_face = None
    for f in bm.faces:
        center = mathutils.Vector((0, 0, 0))
        for v in f.verts:
            center += mw @ v.co
        center /= len(f.verts)
        if center.z > max_z:
            max_z = center.z
            best_face = f
    
    for f in bm.faces:
        f.select_set(False)
    best_face.select_set(True)
    bmesh.update_edit_mesh(mesh)

    bpy.ops.mesh.faces_select_linked_flat(sharpness=math.radians(sharpness))

    bpy.ops.mesh.select_all(action='INVERT')
    bpy.ops.mesh.delete(type='FACE')
    bm = bmesh.from_edit_mesh(mesh)
    loose_verts = [v for v in bm.verts if not v.link_faces]
    if loose_verts:
        bmesh.ops.delete(bm, geom=loose_verts, context='VERTS')
    bmesh.update_edit_mesh(mesh)

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_auto_smooth()
    return True


def assign_material(obj, material_name='grid'):
    mat = bpy.data.materials.get(material_name)
    assert mat, f"Material not found: {material_name}"

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cube_project()

    bpy.ops.object.mode_set(mode='OBJECT')
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return True


def link_material(source_obj, target_obj):
    bpy.ops.object.select_all(action='DESELECT')
    target_obj.select_set(True)
    bpy.context.view_layer.objects.active = target_obj

    src_uv_name = source_obj.data.uv_layers.active.name if source_obj.data.uv_layers else "UVMap"
    if not target_obj.data.uv_layers:
        target_obj.data.uv_layers.new(name=src_uv_name)
    mod = target_obj.modifiers.new(name="TransferUV", type='DATA_TRANSFER')
    mod.object = source_obj
    mod.use_loop_data = True
    mod.data_types_loops = {'UV'}
    bpy.ops.object.modifier_apply(modifier=mod.name)

    if not source_obj.data.materials:
        return True
    mat = source_obj.data.materials[0]
    target_obj.data.materials.clear()
    target_obj.data.materials.append(mat)
    for poly in target_obj.data.polygons:
        poly.material_index = 0

    if target_obj.data.uv_layers:
        target_obj.data.uv_layers.active = target_obj.data.uv_layers[0]
    target_obj.data.update_tag()
    bpy.context.view_layer.update()

    return True

def render_and_save(filepath, hide_obj=None):
    scene = bpy.context.scene
    r = scene.render
    r.image_settings.file_format = 'PNG'
    r.image_settings.color_mode = 'BW'
    r.image_settings.color_depth = '16'
    r.image_settings.compression = 0
    r.image_settings.color_management = 'OVERRIDE'
    scene.display_settings.display_device = 'sRGB'
    vs = scene.view_settings
    vs.view_transform = 'AgX'
    vs.look = 'None'
    vs.exposure = 0.0
    vs.gamma = 1.0
    vs.use_curve_mapping = False
    scene.render.film_transparent = True

    if hide_obj is not None:
        hide_obj.hide_render = True
    bpy.ops.render.render(use_viewport=False)
    img = bpy.data.images.get("Render Result")
    if img:
        img.save_render(filepath=filepath)
        return True
    return False
