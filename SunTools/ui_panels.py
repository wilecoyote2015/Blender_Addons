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

class PanelMovieManager(bpy.types.Panel):
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "SunTools"
    bl_label = "Movie Manager"

    def draw(self, context):
        scn = context.scene.suntools_info
        layout = self.layout

        # TODO: Show only if master scene exists
        if not scn.timeline:
            row = layout.row()
            row.operator( "sequencer.moviemanager_switch_back_to_timeline" )

            # if scn.source_path != "none":
            #     row = layout.row()
            #     col = row.column()
            #     col.operator( "sequencer.moviemanager_hide" )
            #     row.prop(scn, "good_clip" )


        row = layout.row()
        col = row.column()
        print(scn.timeline)
        if not scn.timeline:
            col.operator( "sequencer.moviemanager_insert_strip_masterscene" )
            row = layout.row()
            row.operator( "sequencer.moviemanager_set_timeline" )

        if bpy.context.scene.sequence_editor.active_strip and bpy.context.scene.sequence_editor.active_strip.type == 'META':
            row = layout.row()
            col = row.column()
            col.operator("sequencer.moviemanager_unmeta")


        row = layout.row()

        if scn.timeline:
            row.prop( scn, "show_options" )

            if scn.show_options:

                row = layout.row()
                col = row.column()
                col.prop( scn, "channel" )

                row = layout.row()
                col = row.column()

                # col.prop( scn, "editing_screen" )
                # col.prop( scn, "editing_range_screen" )
                # comp screen selector
                col.prop(scn, "enum_range_screen")

                # editing screen selector
                col.prop(scn, "enum_edit_screen")

                row = layout.row()
                row.prop(scn, "meta")

                # row.prop( scn, "custom_screen" )
                # col.prop( scn, "zoom" )

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

        col.operator( "sequencer.trimtools_cut_current" )
        row.operator( "sequencer.trimtools_snap_end" )

        row = layout.row()
        col = row.column()
        col.operator( "sequencer.trimtools_trim_left" )
        row.operator( "sequencer.trimtools_trim_right" )
