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

import bpy

class CompPanel(bpy.types.Panel):
    bl_label = "Edit strip with Compositor"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_category = "Edit Strip with Compositor"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return bpy.context.scene.sequence_editor is not None

    def draw(self, context):
        scn = context.scene
        activestrip = scn.sequence_editor.active_strip
        layout = self.layout
        # try:
        eswc_info = scn.eswc_info
        if activestrip is not None:
            if activestrip.type == "SCENE":
                layout.operator("sequencer.eswc_switch_to_composite")
            if activestrip.type in {"MOVIE", "IMAGE"}:
                layout.operator("sequencer.eswc_single_comp")

        layout.prop(eswc_info, "bool_show_options")
        if eswc_info.bool_show_options:
            box = layout.box()
            col = box.column(align=True)
            col.prop(eswc_info, "settings")
            col.prop(eswc_info, "bool_show_compositions")
            col.prop(eswc_info, "bool_reuse_compositions")
            col.prop(eswc_info, "bool_add_viewer")
            col.prop(eswc_info, "bool_add_scale")
            col.prop(eswc_info, "bool_use_high_bit_depth_fix")

            col.prop(eswc_info, "bool_auto_proxy")
            if eswc_info.bool_auto_proxy:
                col.prop(eswc_info, "pq")

            if len(bpy.data.node_groups) != 0:
                col.prop(eswc_info, "bool_add_group")
                if eswc_info.bool_add_group:
                    # node group selector
                    col.prop(eswc_info, "enum_node_groups")

            box = layout.box()
            col = box.column(align=True)

            # comp screen selector
            col.prop(eswc_info, "enum_comp_screen")

            # editing screen selector
            col.prop(eswc_info, "enum_edit_screen")


class NodePanel(bpy.types.Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Edit strip with Compositor"
    bl_category = "Edit Strip with Compositor"

    def draw(self, context):
        scn = context.scene
        try:
            layout = self.layout
            row = layout.row()
            col = row.column()
            try:
                col.operator("node.eswc_switch_back_to_timeline")
                col.operator("node.eswc_switch_to_composite_nodepanel")
            except KeyError:
                pass
        except AttributeError:
            pass

