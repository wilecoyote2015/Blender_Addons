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

class PanelMovieManagerBrowser(bpy.types.Panel):
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOLS"
    bl_label = "Movie Manager"
    bl_category = "SunTools"

    def draw(self, context):
        scn = context.scene.suntools_info
        layout = self.layout

        if scn.timeline:
            row = layout.row()
            col = row.column()
            col.prop( scn, "p100" )
            row.prop( scn, "p75" )
            row.prop( scn, "p50" )
            row.prop( scn, "p25" )
            row = layout.row()
            col = row.column()
            col.operator( "file.moviemanager_proxy")
            row = layout.row()
            row.prop(scn, 'proxy_recursive')

        row = layout.row()
        col = row.column()
        col.operator( "file.moviemanager_edit_range" )


class PanelDarktable(bpy.types.Panel):
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "SunTools"
    bl_label = "Darktable"

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        activestrip = scn.sequence_editor.active_strip

        row = layout.row()
        row.prop(scn.suntools_info, 'render_darktable')

        if activestrip.type == 'MOVIE':
            row = layout.row()

            row.prop(activestrip, "use_darktable")
            row = layout.row()
            row.operator("sequencer.darktable_open_darktable_strip")
            row = layout.row()
            row.operator("sequencer.copy_darktable_style")


class PanelMovieManager(bpy.types.Panel):
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "SunTools"
    bl_label = "Movie Manager"

    def draw(self, context):
        scn = context.scene.suntools_info
        layout = self.layout

        row = layout.row()
        # col = row.column()
        if not scn.timeline:
            row.operator( "sequencer.moviemanager_switch_back_to_timeline" )
            row = layout.row()
            row.operator( "sequencer.moviemanager_insert_strip_masterscene" )
            row = layout.row()
            row.operator( "sequencer.moviemanager_set_timeline" )

        row = layout.row()

        if scn.timeline:
            row.prop( scn, "show_options" )

            if scn.show_options:

                row = layout.row()
                col = row.column()
                col.prop( scn, "channel" )

                row = layout.row()
                col = row.column()

                col.prop(scn, "p100_edit_range")
                row.prop(scn, "p75_edit_range")
                row.prop(scn, "p50_edit_range")
                row.prop(scn, "p25_edit_range")

class PanelTrimTools(bpy.types.Panel):
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "SunTools"
    bl_label = "Trim Tools"

    def draw(self, context):
        scn = context.scene.suntools_info
        layout = self.layout

        row = layout.row()
        col = row.column()

        col.operator( "sequencer.trimtools_select_current" )
        row.prop( scn, "select_audio" )

        row = layout.row()
        col = row.column()

        # col.operator( "sequencer.trimtools_cut_current" )
        row.operator( "sequencer.trimtools_snap_end" )

        row = layout.row()
        col = row.column()
        col.operator( "sequencer.trimtools_trim_left" )
        row.operator( "sequencer.trimtools_trim_right" )


class CompPanel(bpy.types.Panel):
    bl_label = "Edit strip with Compositor"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_category = "SunTools"
    bl_region_type = "UI"

    def draw(self, context):
        scn = context.scene
        activestrip = scn.sequence_editor.active_strip
        layout = self.layout
        # try:
        eswc_info = scn.eswc_info
        if activestrip is not None:
            if activestrip.type == "META" and activestrip.is_composite:
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
            col.prop(eswc_info, "bool_use_high_bit_depth_fix")

            if len(bpy.data.node_groups) != 0:
                col.prop(eswc_info, "bool_add_group")
                if eswc_info.bool_add_group:
                    # node group selector
                    col.prop(eswc_info, "enum_node_groups")

class NodePanel(bpy.types.Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Edit strip with Compositor"
    bl_category = "SunTools"

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
