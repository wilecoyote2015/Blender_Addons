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
from CompositeVSE import common_functions
import os

# FIXME: Numerous issues when toggling composition visibility. Best to rewrite it.
#   Maybe. when creating composition, do not replace movie by composition, but instead create
#   meta strip with both. Then toggling simply hides/unhides composition strip.
#   this way, there is no hassle with transferring all the properties (except when creating the metastrip, where all
#   connections to modifier strips etc. must be reconnected and trafo / keyframes / modifiers must be transferred (
#   remember to remove those from the original strip!)
#   For transition etc. sequences, simply search all sequences whether they have input_1 or input_2 field and if the
#   value referes to the source sequence, change this to the meta sequence.
#   For keyframes, I have no idea. But see https://docs.blender.org/api/current/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert
#   for modifiers, can one simply copy the  bpy.types.SequenceModifiers struct from source and repace the one of source with an empty one afterwards?
# TODO: composition scene should have render resolution of input file
# TODO: toggling composition visibility: end!

class OperatorCreateCompositionFromStrip(bpy.types.Operator):
    bl_idname = "sequencer.eswc_single_comp"
    bl_label = "Create Comp from strips"

    def copy_comp_render_settings(self, scene_a, scene_b):
        # copy compositor render settings
        scene_a.node_tree.use_opencl = scene_b.node_tree.use_opencl
        scene_a.node_tree.two_pass = scene_b.node_tree.two_pass
        scene_a.node_tree.render_quality = scene_b.node_tree.render_quality
        scene_a.node_tree.edit_quality = scene_b.node_tree.edit_quality
        scene_a.node_tree.chunk_size = scene_b.node_tree.chunk_size

    def create_composition_for_strip(self, original_strip, context):
        # Creates new scene but doesn't set it as active.
        # attention: new_scene_name may be != new_scene.name, if scene of same name already exists.
        editing_scene = context.scene

        new_scene_name = '{}{}'.format('Comp_', original_strip.name)
        bpy.ops.scene.new(type='LINK_COPY')
        new_scene = context.scene
        new_scene.name = new_scene_name
        # new_scene = bpy.data.scenes.new(new_scene_name)

        # editing_scene = context.scene
        eswc_info_editing = editing_scene.eswc_info

        # Change render settings for new scene to match original scene
        # self.copy_render_settings(new_scene, editing_scene)

        # set render resolution to full so that scaling is done in sequencer
        new_scene.render.resolution_percentage = 100

        if original_strip.type in ('MOVIE', 'MOVIECLIP'):
            print(original_strip.fps)
            new_scene.render.fps_base = int(round(original_strip.fps)) / original_strip.fps
            new_scene.render.fps = int(round(original_strip.fps))

        # new_scene.render.resolution_x = original_strip.resolution_x
        # new_scene.render.resolution_y = original_strip.resolution_y

        # Setup new scene EndFrame to match original_strip length
        new_scene.frame_end = int(original_strip.frame_final_duration + original_strip.frame_offset_start + original_strip.frame_offset_end)

        # Setup nodes
        new_scene.use_nodes = True

        self.create_node_tree_for_strip(new_scene, original_strip, eswc_info_editing)

        new_scene.eswc_info.master_scene = editing_scene.name
        new_scene.eswc_info.type_original_strip = original_strip.type
        new_scene.eswc_info.path_input = common_functions.get_filepath_strip(original_strip)
        bpy.context.window.scene = editing_scene

        # context.screen.scene.update()

        return new_scene

    def create_node_tree_for_strip(self, new_scene, strip, eswc_info):
        # copy_comp_render_settings(new_scene, cur_scene)
        node_tree = new_scene.node_tree

        # Clear default nodes
        for node in node_tree.nodes:
            node_tree.nodes.remove(node)

        # Create input node
        image_node = node_tree.nodes.new('CompositorNodeImage')
        image_node.location = 0, 0

        if strip.type == 'IMAGE':
            # Find extension
            full_name = strip.elements[0].filename
            extension = os.path.splitext(full_name)[1]

            # Get source of strip and add strip path
            clean_path = bpy.path.abspath(strip.directory)
            files = []
            for file in os.listdir(clean_path):
                if file.endswith(extension):
                    files.append(file)
            path = os.path.join(clean_path, full_name)
            # Check for existing image datablocks for this item
            bool_create_new = True
            for image in bpy.data.images:
                if image.name == full_name:
                    strip_source = bpy.data.images[full_name]
                    bool_create_new = False

            # or create a new one
            if bool_create_new:
                strip_path = bpy.path.resolve_ncase(path)
                strip_source = bpy.data.images.load(strip_path)
                strip_source.source = 'SEQUENCE'
            image_node.image = strip_source

            image_node.image.source = 'SEQUENCE'
            image_node.frame_duration = len(files)

        elif strip.type == 'MOVIE':
            # Get source of strip and add strip path
            strip_path = strip.filepath

            # Check for existing image datablocks for this item
            bool_create_new = True
            D = bpy.data
            for file in D.images:
                if file.filepath == strip_path:
                    strip_source = bpy.data.images[file.name]
                    bool_create_new = False
            # or create a new one
            if bool_create_new:
                strip_source = bpy.data.images.load(strip_path)
                strip_source.source = 'MOVIE'
            image_node.image = strip_source

        # use colorspace of source file
        image_node.image.colorspace_settings.name = strip.colorspace_settings.name

        print(image_node.image.size)
        new_scene.render.resolution_x = int(image_node.image.size[0])
        new_scene.render.resolution_y = int(image_node.image.size[1])

        # Other input settings
        # length shall be original movie length.
        # todo: is this necessary? Doesn't the strip have the duration by default?
        # todo: why set frame offset?
        image_node.frame_duration = int(strip.frame_final_duration + \
                                    strip.frame_offset_start + strip.frame_offset_end + \
                                    strip.animation_offset_end)
        image_node.frame_offset = int(strip.animation_offset_start)

        image_node.use_cyclic = False
        image_node.use_auto_refresh = True

        # # Update scene
        # new_scene.update()

        # new_scene.frame_current = 2

        # create scale node
        if eswc_info.bool_add_scale:
            scale = node_tree.nodes.new('CompositorNodeScale')
            scale.space = "RENDER_SIZE"
            scale.location = 180, 0

        # create group node
        if eswc_info.bool_add_group:
            group_exists = False
            nodegroup = ""

            for file, elem in enumerate(bpy.data.node_groups):
                if file == int(eswc_info.enum_node_groups):
                    group_exists = True
                    nodegroup = elem
                    break

            if group_exists == True:
                group = node_tree.nodes.new('CompositorNodeGroup')
                group.node_tree = nodegroup
                group.location = 350, 0

        # create comp and viewer output node
        comp = node_tree.nodes.new('CompositorNodeComposite')
        if eswc_info.bool_add_group and group_exists:
            comp.location = 600, 0
        else:
            comp.location = 400, 0
        if eswc_info.bool_add_viewer:
            viewer = node_tree.nodes.new('CompositorNodeViewer')
            reroute = node_tree.nodes.new('NodeReroute')
            if eswc_info.bool_add_group and group_exists:
                reroute.location = 550, -150
                viewer.location = 600, -200
            else:
                reroute.location = 350, -150
                viewer.location = 400, -200

        # Link nodes
        links = node_tree.links
        if not eswc_info.bool_add_viewer:
            if eswc_info.bool_add_group and group_exists:
                if eswc_info.bool_add_scale:
                    link = links.new(image_node.outputs[0], scale.inputs[0])
                    link = links.new(scale.outputs[0], group.inputs[0])
                    link = links.new(group.outputs[0], comp.inputs[0])
                else:
                    link = links.new(image_node.outputs[0], group.inputs[0])
                    link = links.new(group.outputs[0], comp.inputs[0])
            else:
                if eswc_info.bool_add_scale:
                    link = links.new(image_node.outputs[0], scale.inputs[0])
                    link = links.new(scale.outputs[0], comp.inputs[0])
                else:
                    link = links.new(image_node.outputs[0], comp.inputs[0])
        else:
            link = links.new(reroute.outputs[0], viewer.inputs[0])
            link = links.new(reroute.outputs[0], comp.inputs[0])
            if eswc_info.bool_add_group == True and group_exists == True:
                if eswc_info.bool_add_scale:
                    link = links.new(image_node.outputs[0], scale.inputs[0])
                    link = links.new(scale.outputs[0], group.inputs[0])
                    link = links.new(group.outputs[0], reroute.inputs[0])

                else:
                    link = links.new(image_node.outputs[0], group.inputs[0])
                    link = links.new(group.outputs[0], reroute.inputs[0])
            else:
                if eswc_info.bool_add_scale:
                    link = links.new(image_node.outputs[0], scale.inputs[0])
                    link = links.new(scale.outputs[0], reroute.inputs[0])
                else:
                    link = links.new(image_node.outputs[0], reroute.inputs[0])

    def invoke(self, context, event):
        eswc_info = context.scene.eswc_info

        selected_strips = context.selected_sequences

        # Loop selected strips
        names_strips_failed = []
        for strip in selected_strips:

            # Check if strip is a movie
            if strip.type in ['MOVIE', 'IMAGE']:

                # create a new composition if no composition exists or if one or more compositions exist and
                # option to create new compositions is activated.
                # generate the composition
                reuse_compositions = eswc_info.bool_reuse_compositions
                matching_compositions = common_functions.find_matching_compositions(strip)
                if len(matching_compositions) == 0 or not reuse_compositions:
                    comp_scene = self.create_composition_for_strip(strip, context)
                elif len(matching_compositions) == 1 and reuse_compositions:
                    # If only one compostion exists for the source, it can be reused
                    comp_scene = matching_compositions[0]
                else:
                    names_strips_failed.append(strip.name)
                    continue

                # insert the strip into the scene in place of the original if composite strips are to be shown.
                # else, set the name of the scene
                if eswc_info.bool_show_compositions:
                    strip_composite = common_functions.insert_scene_timeline(new_scene=comp_scene,
                                                           original_strip=strip, 
                                                           context=context)
                else:
                    strip.composite_scene = comp_scene.name

            else:
                print("Active Strip is not a movie or an image sequence.")

        if len(names_strips_failed) > 0:
            self.report({'ERROR_INVALID_INPUT'}, 'The following strips could not be converted because more than one'
                                                 'composite scenen with the same source exists and \"Reuse Composition\"'
                                                 'is activated: {}'.format(str(names_strips_failed)))
        return {'FINISHED'}
    

