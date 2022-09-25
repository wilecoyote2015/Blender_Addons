# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

from SunTools import common_functions
import bpy


class SwitchToCompositeBase(bpy.types.Operator):
    def get_scene_from_composite_meta(self, strip_meta):
        if strip_meta.type == 'META' and strip_meta.is_composite:
            for strip_in_meta in strip_meta.sequences:
                if strip_in_meta.type == 'SCENE':
                    return strip_in_meta.scene
        return None

    def switch_to_composite_scene(self, scene_composition):
        # TODO: set the current frame in the comp scene to match the current
        #   position of the playead in the master scene if the playhead is on the strip
        bpy.context.window.scene = scene_composition
        try:
            viewer = bpy.context.scene.node_tree.nodes['Viewer']
            bpy.context.scene.node_tree.nodes.active = viewer
        except KeyError:
            pass
        bpy.context.scene.frame_current = bpy.context.scene.frame_start


class Switch_to_Composite_Operator(SwitchToCompositeBase):
    bl_idname = "sequencer.eswc_switch_to_composite"
    bl_label = "Edit Composition"

    def invoke(self, context, event):
        strip_active = context.scene.sequence_editor.active_strip
        scene_composition = self.get_scene_from_composite_meta(strip_active)
        if scene_composition is None:
            return
        scn = context.scene

        eswc_info = scn.eswc_info
        eswc_info.edit_screen = bpy.context.window.workspace.name
        if eswc_info.comp_screen:
            workspace = eswc_info.comp_screen
        else:
            workspaces = common_functions.avail_screens()
            workspace = workspaces[0][0]

            for ws in workspaces:
                if 'comp' in ws[0].lower():
                    workspace = ws[0]

        common_functions.switch_screen(
            context,
            workspace
        )
        self.switch_to_composite_scene(scene_composition)

        return {'FINISHED'}


class Switch_to_Composite_Nodepanel_Operator(SwitchToCompositeBase):
    bl_idname = "node.eswc_switch_to_composite_nodepanel"
    bl_label = "Edit Composition"

    def invoke(self, context, event):
        master_scene = bpy.data.scenes[context.scene.eswc_info.master_scene]

        scene_composition = self.get_scene_from_composite_meta(master_scene.sequence_editor.active_strip)
        if scene_composition is None:
            return
        eswc_info = master_scene.eswc_info

        eswc_info.comp_screen = bpy.context.window.workspace.name
        self.switch_to_composite_scene(scene_composition)

        return {'FINISHED'}


class Switch_back_to_Timeline_Operator(bpy.types.Operator):
    bl_idname = "node.eswc_switch_back_to_timeline"
    bl_label = "Get Back"

    def invoke(self, context, event):
        scn = bpy.data.scenes[context.scene.eswc_info.master_scene]

        # this is to avoid errors when changing percentage for preview render...
        context.scene.render.resolution_percentage = 100

        eswc_info = scn.eswc_info
        eswc_info.comp_screen = bpy.context.window.workspace.name
        common_functions.switch_screen(context, eswc_info.edit_screen)
        context.window.scene = scn

        return {'FINISHED'}
