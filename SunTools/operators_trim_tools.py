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

    def get_strips_current_frame(self, context):
        current_frame = bpy.context.scene.frame_current
        
        sequences_current_frame = []
        sequences_ignore = []  # sound strips of pairs
        partners = {}
        
        for sequence in context.scene.sequence_editor.sequences:
            if (sequence.frame_final_start <= current_frame 
                    and sequence.frame_final_end > current_frame
                    and sequence not in sequences_ignore
            ):
                partners_sequence = self.find_movie_sound_pair(sequence)
                if partners_sequence is not None:
                    sequences_ignore.append(partners_sequence[1])
                    sequences_current_frame.append(partners_sequence[0])
                    partners[partners_sequence[0].name] = partners_sequence[1]
                else:
                    sequences_current_frame.append(sequence)
                    
        return sequences_current_frame, partners
                
    def find_movie_sound_pair(self, sequence):

        movie, sound = None, None

        for sequence_candidate in bpy.context.scene.sequence_editor.sequences:
            if (sequence.frame_final_start == sequence_candidate.frame_final_start
                and sequence.frame_final_end == sequence_candidate.frame_final_end
                and sequence_candidate is not sequence
            ):
                if sequence.type in ['MOVIE', 'MOVIECLIP'] and sequence_candidate.type == 'SOUND':
                    # if more than one result found, it is invalid
                    if movie is not None or sound is not None:
                        return None
                    movie, sound = sequence, sequence_candidate
                elif sequence_candidate.type in ['MOVIE', 'MOVIECLIP'] and sequence.type == 'SOUND':
                    # if more than one result found, it is invalid
                    if movie is not None or sound is not None:
                        return None
                    movie, sound = sequence_candidate, sequence
                
        return movie, sound if movie and sound else None


    def invoke (self, context, event):
        # find all strips at current cursor, but exclude pairs
        strips_current_frame, partner_strips = self.get_strips_current_frame(context)
        
        # sort by channel
        strips_current_frame_sorted = sorted(strips_current_frame, key=lambda x: x.channel)

        # get index of last selected strip in the list
        indices_selected = []
        for index, strip in enumerate(strips_current_frame_sorted):
            if strip.select:
                indices_selected.append(index)
                
        if indices_selected:
            if indices_selected[-1] < len(strips_current_frame_sorted) - 1:
                index_strip_select = indices_selected[-1] + 1
            else:
                index_strip_select = None
                
        else:
            index_strip_select = 0

        bpy.ops.sequencer.select_all(action='DESELECT')
        
        if index_strip_select is not None and strips_current_frame_sorted:
            print(index_strip_select)
            print(strips_current_frame_sorted)
            strip_to_select = strips_current_frame_sorted[index_strip_select]
            strip_to_select.select = True
            
            if strip_to_select.name in partner_strips:
                partner_strips[strip_to_select.name].select = True

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
