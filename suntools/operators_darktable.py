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
import os
from subprocess import run
from tempfile import TemporaryDirectory
from .common_functions import render_current_frame_strip_to_image
from bpy_extras.io_utils import ExportHelper, ImportHelper

# TODO: Support loading / saving xmp files per strip.
#   maybe, when loading xmp file, do not store the xmp as string, but simply refer to
#   filepath

# TODO: Option to define custom .conf dir so that it can be saved with the project directory
#   and ensures reproductibility across systems.

# FIXME: Sometimes, strip positions and start frames get messed up during rendering.
#   seems to happen when cancelling render at certain points. Tried to register render cancel handler,
#   but did not solve the issue
#   try to set start and end frame directly again in pre_render after assigning new source
#   Update: done now. Seems to work for correct rendering, but strip display still glitches and
#   if rendering is aborted, often even the source file is not changed back from temporary file to original source.
#   is the render abort handler not called properly?

# TODO: option for color space selection

class OperatorOpenDarktable(bpy.types.Operator):
    bl_idname = "sequencer.darktable_open_darktable_strip"
    bl_label = "Edit with Darktable"
    bl_description = "Open the Strip in Darktable for color grading. " \
                     "IMPORTANT: There must not be a running Darktable instance before using the operator." \
                     "Darktable must be closed when Editing is finished. Blender Freezes until Darktable is closed." \
                     "Darktable and ffmpeg must be in your PATH."

    def invoke(self, context, event ):
        # render the current frame of selected strip via FFMPEG
        current_strip = bpy.context.scene.sequence_editor.active_strip
        with TemporaryDirectory() as path_tempdir:
            # TODO: tiff output is 16 bit if input video is 10 bit.
            #   however, it may be appropriate to always force 16 bit output
            #   in case that ffmpeg's default behavior changes.
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
    bl_description = "Transfer Darktable style from active strip to all selected strips"

    def invoke(self, context, event ):
        # render the current frame of selected strip via FFMPEG
        current_strip = bpy.context.scene.sequence_editor.active_strip
        for sequence in bpy.context.scene.sequence_editor.sequences:
            if sequence.select and sequence.type == 'MOVIE':
                sequence.xmp_darktable = current_strip.xmp_darktable

        return {'FINISHED'}

class OperatorLoadXmpDarktable(bpy.types.Operator, ImportHelper):
    bl_idname = "sequencer.load_darktable_style"
    bl_label = "Load XMP"
    bl_description = "Load XMP and apply it to all selected strips"

    filepath = bpy.props.StringProperty()

    filename_ext = ".xmp"

    filter_glob: bpy.props.StringProperty(
        default="*.xmp",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        with open(str(self.filepath)) as f:
            xmp = f.read()

        for sequence in bpy.context.scene.sequence_editor.sequences:
            if sequence.select and sequence.type == 'MOVIE':
                sequence.xmp_darktable = xmp

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class OperatorSaveXmpDarktable(bpy.types.Operator, ExportHelper):
    bl_idname = "sequencer.save_darktable_style"
    bl_label = "Save XMP"
    bl_description = "Save the XMP of the active strip to file"

    filename_ext = ".xmp"

    filter_glob: bpy.props.StringProperty(
        default="*.xmp",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    def execute(self, context):
        current_strip = bpy.context.scene.sequence_editor.active_strip
        if current_strip:
            if current_strip.xmp_darktable == '':
                raise ValueError('Active Strip has no Darktable data.')
            print(os.path.splitext(self.filepath)[0] + '.xmp')
            with open(os.path.splitext(str(self.filepath))[0] + '.xmp', 'w') as f:
                f.write(current_strip.xmp_darktable)
        else:
            raise ValueError('No active strip.')


        return {'FINISHED'}
