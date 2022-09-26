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

from SunTools.common_functions import get_masterscene, detect_strip_type, switch_workspace, insert_clip, avail_screens
import bpy
import json
import os
from subprocess import run
from tempfile import TemporaryDirectory
from SunTools.common_functions import render_current_frame_strip_to_image



# TODO: Support loading / saving xmp files per strip.
#   maybe, when loading xmp file, do not store the xmp as string, but simply refer to
#   filepath

class OperatorOpenDarktable(bpy.types.Operator):
    bl_idname = "sequencer.darktable_open_darktable_strip"
    bl_label = "Edit with Darktable"

    def invoke(self, context, event ):
        # render the current frame of selected strip via FFMPEG
        current_strip = bpy.context.scene.sequence_editor.active_strip
        with TemporaryDirectory() as path_tempdir:
            filename_output = f'{current_strip.name}.tiff'
            path_output = str(os.path.join(path_tempdir, filename_output))
            render_current_frame_strip_to_image(current_strip, bpy.context.scene, path_output)

            path_xmp = os.path.join(path_tempdir, filename_output + '.xmp')

            if current_strip.xmp_darktable != '':
                with open(path_xmp, 'w') as f:
                    f.write(current_strip.xmp_darktable)

            cmd = [
                'darktable',
                path_output
            ]

            run(cmd)

            if os.path.isfile(path_xmp):
                with open(path_xmp) as f:
                    current_strip.xmp_darktable = f.read()
            else:
                return {'ERROR'}

        return {'FINISHED'}

class OperatorCopyDarktableStyle(bpy.types.Operator):
    bl_idname = "sequencer.copy_darktable_style"
    bl_label = "Transfer darktable style."

    def invoke(self, context, event ):
        # render the current frame of selected strip via FFMPEG
        current_strip = bpy.context.scene.sequence_editor.active_strip
        for sequence in bpy.context.scene.sequence_editor.sequences:
            if sequence.selected and sequence.type == 'MOVIE':
                sequence.xmp_darktable = current_strip.xmp_darktable

        return {'FINISHED'}