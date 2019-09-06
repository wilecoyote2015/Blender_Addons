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

class OperatorSelectCurrent (bpy.types.Operator):
    bl_idname = "sequencer.trimtools_select_current"
    bl_label = "Select current Strip"
    bl_description = "Select the Strip on the current frame"

    def invoke (self, context, event):
        channel = 0
        current_frame = bpy.context.scene.frame_current
        is_already_selection = False
        channel_of_selected_strip = 0
        something_is_selected = False
        first_selected_strip = None

        # find out whether an appropiate strip is already selected
        for sequence in bpy.context.scene.sequence_editor.sequences:
            if (sequence.type == 'MOVIE' or sequence.type == 'SCENE' or sequence.type == 'MOVIECLIP' or sequence.type == 'IMAGE' or sequence.type == 'COLOR' or sequence.type == 'MULTICAM'):
                if (sequence.frame_final_start <= current_frame and sequence.frame_final_end >= current_frame):
                    if (sequence.select == True):
                        first_selected_strip = sequence
                        is_already_selection = True
                        break

        for sequence in bpy.context.scene.sequence_editor.sequences:
            if (sequence.type == 'MOVIE' or sequence.type == 'SCENE' or sequence.type == 'MOVIECLIP' or sequence.type == 'IMAGE' or sequence.type == 'COLOR' or sequence.type == 'MULTICAM'):
                if (sequence.frame_final_start <= current_frame and sequence.frame_final_end >= current_frame):
                    if (sequence.channel > channel and is_already_selection == False):
                        bpy.ops.sequencer.select_all(action='DESELECT')
                        bpy.context.scene.sequence_editor.active_strip = sequence
                        sequence.select = True
                        channel = sequence.channel
                        selectedstrip = sequence
                        something_is_selected = True
                    elif (sequence.channel < first_selected_strip.channel and sequence.channel > channel_of_selected_strip and is_already_selection == True):
                        bpy.ops.sequencer.select_all(action='DESELECT')
                        bpy.context.scene.sequence_editor.active_strip = sequence
                        sequence.select = True
                        channel = sequence.channel
                        selectedstrip = sequence
                        channel_of_selected_strip = sequence.channel
                        something_is_selected = True

        if (something_is_selected == False and is_already_selection == True):
            bpy.ops.sequencer.select_all(action='DESELECT')

        # select the audio of the strip.
        # do selection by duration and position and not by name to cover case of externally recorded audio
        for sequence in bpy.context.scene.sequence_editor.sequences:
            if (sequence.type == 'SOUND' and something_is_selected == True and bpy.context.scene.select_audio == True):
                if (sequence.frame_final_start == selectedstrip.frame_final_start and sequence.frame_final_end == selectedstrip.frame_final_end):
                        sequence.select = True

        return {'FINISHED'}
        
class OperatorCutCurrent(bpy.types.Operator):
    bl_idname = "sequencer.trimtools_cut_current"
    bl_label = "Cut current Strip"
    bl_description = "Cut the Strip on the current frame"

    def invoke (self, context, event):
        bpy.ops.sequencer.trimtools_select_current()

        current_frame = bpy.context.scene.frame_current
        bpy.ops.sequencer.cut(frame=current_frame)

        return {'FINISHED'}


class OperatorTrimLeft(bpy.types.Operator):
    bl_idname = "sequencer.trimtools_trim_left"
    bl_label = "Trim Left"
    bl_description = "Set the selected clip's starting frame to current frame"

    def invoke (self, context, event):
        for selected_sequence in bpy.context.selected_sequences:
            selected_sequence.frame_final_start = bpy.context.scene.frame_current
        return {'FINISHED'}


class OperatorTrimRight(bpy.types.Operator):
    bl_idname = "sequencer.trimtools_trim_right"
    bl_label = "Trim Right"
    bl_description = "Set the selected clip's ending frame to current frame"

    def invoke (self, context, event):
        for selected_sequence in bpy.context.selected_sequences:
            selected_sequence.frame_final_end = bpy.context.scene.frame_current
        return {'FINISHED'}


class OperatorSnapEnd (bpy.types.Operator):
    bl_idname = "sequencer.trimtools_snap_end"
    bl_label = "Snap End"
    bl_description = "Snap the Clip to the current frame with it´s end"

    def invoke (self, context, event):
        for selected_sequence in bpy.context.selected_sequences:
            selected_sequence.frame_start = bpy.context.scene.frame_current - selected_sequence.frame_offset_start - selected_sequence.frame_final_duration
        return {'FINISHED'}
