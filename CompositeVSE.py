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
"""
TODO: Compositinng mit den den Ganzen sachen:
 - Beim Composite erstellen:
    - Wenn Reuse Composite:
        - Nach Composites, die den selben Quellclip haben, suchen
            - Wenn keine vorhanden:
                - Neue Composition erstellen
                - Clipquelle in Composite speichern
            - Wenn eine vorhanden: Diesen nehmen
            - Wenn mehrere vorhanden: Nichts tun und am ende warnung ausgeben.
            Dass diese(r) clip(s) nicht gecomposited werden konnten,
            sodass man das manuell mit nur einer selektion machen soll.
    - Sonst:
        - Neue Comp erstellen
        - Clipquelle in Comp speichern

    - Wenn im Comp=Preview Modus:
        - Clipnamen(oder besser ID) speichern
        - Clip loeschen
        - Composite clip einfuegen
        - Quellen aller Effektstrips updaten
    - Sonst:
        - Compname im Clip speichern

- Beim Wechsel zwischen Comp-Preview und normal:
    - Von Comp-Preview:
        - Comp-Strip loeschen
        - Movieclip mit der Quelldatei erstellen
        - Quellen aller Effektstrips updaten
    - Nach Comp-Preview:
        - Comp-Name von Moviestrip holen
        - Moviestrip loeschen
        - Composite einfuegen
        - Quellen aller Effektstrips updaten

Notizen:
- Allgemeine Funktion  fuer das Einfuegen einer existierenden Komposition
    Als ersatz eines Movieclips schreiben. Die wird beim Wechsel und beim Einfuegen verwendet.
- Beim einfuegen von CLips gibt es die Option "replace_sel". Kann man die verwenden?

"""

# TODO: Correctly handle image sequences which start at a frame number >0. The correct offset has to be set.

bl_info = {
    "name": "Edit Strip With Compositor REMAKE f",
    "description": "Send one or more Sequencer strips to the Compositor, gently",
    "author": "Carlos Padial, TMW, Björn Sonnenschein",
    "version": (0, 14),
    "blender": (2, 78),
    "location": "Sequencer > UI panel, Node Editor > UI panel",
    "wiki_url": "None Yet"
                "None Yet",
    "tracker_url": "None"
                   "func=detail&aid=<number>",
    "category": "Sequencer"}

import bpy, os

from bpy.props import (IntProperty,
                       FloatProperty,
                       EnumProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty,
                       PointerProperty,
                       )

# common functions
def triminout(strip, sin, sout):
    start = strip.frame_start + strip.frame_offset_start
    end = start + strip.frame_final_duration
    if end > sin:
        if start < sin:
            strip.select_right_handle = False
            strip.select_left_handle = True
            bpy.ops.sequencer.snap(frame=sin)
            strip.select_left_handle = False
    if start < sout:
        if end > sout:
            strip.select_left_handle = False
            strip.select_right_handle = True
            bpy.ops.sequencer.snap(frame=sout)
            strip.select_right_handle = False
    return {'FINISHED'}


def switch_screen(context, eswc_screen):
    # get the name of the desired composite screen
    for index, screen in enumerate(bpy.data.screens):
        if index == int(eswc_screen):
            screen_name = screen.name
            break

    # change current screen to the composite screen
    for screen in bpy.data.screens:
        bpy.ops.screen.screen_set(delta=1)
        if context.screen.name == screen_name:
            break


# ----------------------------------------------------------------------------
# Persistent Scene Data Types for Edit Strip With Compositor addon (eswc_info)

class ESWC_Info(bpy.types.PropertyGroup):
    comp_name = StringProperty(
        name="Comp Name",
        default="",
        description="Name of the composite")



    bool_show_options = BoolProperty(
        name="Show options",
        description="Show options",
        default=False)

    bool_add_scale = BoolProperty(
        name="Add Scale node",
        description="Add Scale node",
        default=False)

    bool_preserve_duration = BoolProperty(
        name="Preserve strip duration",
        description="If activated, the composite will have the untrimmed instead of trimmed length of the input strip.",
        default=False)

    bool_add_viewer = BoolProperty(
        name="Add Viewer",
        description="You can add a viewer node to the new compositions \
        automatically",
        default=False)

    bool_add_group = BoolProperty(
        name="Add Nodegroup",
        description="You can add a custom node group to the new compositions \
        automatically",
        default=False)

    # the input path of the movie file the composition was created from
    # if it is empty, the operators infer that the current scene
    # is not a composition.
    movie_input = StringProperty(
        name="Movie strip input",
        default="",
        description="the input path of the movie file the composition was \
            created from")

    bool_auto_proxy = BoolProperty(
        name="Automatic proxy settings",
        description="The new scene will automatically create and use a proxy \
        custom directory in the project directory, 100% proxy will be \
        generated by default. ",
        default=False)

    selections = [("All", "All", "Copy all settings"),
                  # ( "Select", "Select", "Copy selected settings" ),
                  ("None", "None", "Copy none of the settings")]
    settings = EnumProperty(
        name="Settings Type",
        items=selections,
        default="All",
        description="Choose which settings to copy from the source clip to the created composition")

    proxy_qualities = [("1", "25%", ""), ("2", "50%", ""),
                       ("3", "75%", ""), ("4", "100%", "")]
    pq = EnumProperty(
        name="Proxy Quality", items=proxy_qualities,
        default="1",
        description="Quality setting for auto proxies")

    channel_increase = IntProperty(
        name="Channel increase",
        description="Define how many tracks above the source strips the new \
        Strips are placed for the single strip option. For the multiple clips \
        option this is the channel number the new strip will be placed in",
        default=1, min=1, max=30, step=1)

    master_scene = StringProperty(
        name="Master Scene",
        description="This is the name of the Scene's Master Scene",
        default="Scene")

    scene_init_comp = BoolProperty(name="",
                                   description="",
                                   default=False)

    # col_node_groups = CollectionProperty(type=StringColl)

    def avail_nodegroups(self, context):
        items = []
        for i, node_group in enumerate(bpy.data.node_groups):
            items.append((str(i), node_group.name, node_group.name))
        return items

    enum_node_groups = EnumProperty(items=avail_nodegroups,
                                    name="Node Group")

    def avail_screens(self, context):
        items = []
        for i, elem in enumerate(bpy.data.screens):
            items.append((str(i), elem.name, elem.name))
        return items

    enum_edit_screen = EnumProperty(items=avail_screens,
                                    name="Editing Screen")

    enum_comp_screen = EnumProperty(items=avail_screens,
                                    name="Compositing Screen")


# Initialization                
def initprops(context, scn):
    eswc_info = scn.eswc_info

    try:
        if eswc_info.scene_init_comp == True:
            return False
    except AttributeError:
        pass
    # Define some new properties we will use
    eswc_info.comp_name = ""  # what is this for?
    eswc_info.bool_show_options = False
    eswc_info.bool_add_scale = False
    eswc_info.bool_preserve_duration = True
    eswc_info.bool_add_viewer = False
    eswc_info.bool_add_group = False
    eswc_info.bool_auto_proxy = False
    eswc_info.settings = "All"
    eswc_info.pq = "1"
    eswc_info.channel_increase = 1
    eswc_info.scene_init_comp = True


class SetMasterSceneOperator(bpy.types.Operator):
    bl_idname = "eswc.set_master_scene"
    bl_label = "Set master scene"

    def invoke(self, context, event):
        bpy.ops.sequencer.rendersize()
        initprops(context, context.scene)

        return {'FINISHED'}

        # ______________________PANEL_______________________________________


class CompPanel(bpy.types.Panel):
    bl_label = "Edit strip with Compositor"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"

    @staticmethod
    def has_sequencer(context):
        return (context.space_data.view_type in {'SEQUENCER'})

    @classmethod
    def poll(self, context):
        try:
            if (bpy.context.scene.sequence_editor.active_strip.type in {'MOVIE', "IMAGE", "SCENE"}):
                return bpy.context.scene.sequence_editor
            else:
                return False
        except:
            return False

    def draw(self, context):
        scn = context.scene
        activestrip = scn.sequence_editor.active_strip
        layout = self.layout
        try:
            eswc_info = scn.eswc_info
            if eswc_info.scene_init_comp:
                if activestrip.type == "SCENE":
                    layout.operator("eswc.switch_to_composite")
                if activestrip.type in {"MOVIE", "IMAGE"}:
                    layout.operator("eswc.single_comp")
                    layout.prop(eswc_info, "bool_show_options")
                    if eswc_info.bool_show_options:
                        box = layout.box()

                        col = box.column(align=True)

                        col.prop(eswc_info, "channel_increase")
                        col.prop(eswc_info, "settings")
                        col.prop(eswc_info, "bool_add_viewer")
                        col.prop(eswc_info, "bool_add_scale")
                        col.prop(eswc_info, "bool_preserve_duration")
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

            else:
                layout.operator("eswc.set_master_scene")
        except AttributeError as Err:
            layout.operator("eswc.set_master_scene")


class NodePanel(bpy.types.Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Edit strip with Compositor"

    def draw(self, context):
        scn = context.scene
        try:
            eswc_info = scn.eswc_info

            layout = self.layout
            row = layout.row()
            col = row.column()
            try:
                col.prop(eswc_info, "comp_name")
                col.operator("eswc.switch_back_to_timeline")
                col.operator("eswc.switch_to_composite_nodepanel")
            except KeyError:
                pass
        except AttributeError:
            pass


class Switch_to_Composite_Operator(bpy.types.Operator):
    bl_idname = "eswc.switch_to_composite"
    bl_label = "Edit Composition"


    def invoke(self, context, event):
        if context.scene.sequence_editor.active_strip.type == 'SCENE':
            stripscene = context.scene.sequence_editor.active_strip.scene
            scn = context.scene

            eswc_info = scn.eswc_info
            switch_screen(context, eswc_info.enum_comp_screen)
            context.screen.scene = stripscene

            try:
                viewer = context.scene.node_tree.nodes['Viewer']
                context.scene.node_tree.nodes.active = viewer
            except KeyError:
                pass
            context.scene.frame_current = context.scene.frame_start

        return {'FINISHED'}


class Switch_to_Composite_Nodepanel_Operator(bpy.types.Operator):
    bl_idname = "eswc.switch_to_composite_nodepanel"
    bl_label = "Edit Composition"

    def invoke(self, context, event):
        master_scene = bpy.data.scenes[context.scene.eswc_info.master_scene]

        if master_scene.sequence_editor.active_strip.type == 'SCENE':
            target_scene = master_scene.sequence_editor.active_strip.scene
            eswc_info = master_scene.eswc_info

            switch_screen(context, eswc_info.enum_comp_screen)
            context.screen.scene = target_scene

            try:
                viewer = context.scene.node_tree.nodes['Viewer']
                context.scene.node_tree.nodes.active = viewer
            except KeyError:
                pass
            context.scene.frame_current = context.scene.frame_start

        return {'FINISHED'}


class Switch_back_to_Timeline_Operator(bpy.types.Operator):
    bl_idname = "eswc.switch_back_to_timeline"
    bl_label = "Get Back"

    def invoke(self, context, event):

        scn = bpy.data.scenes[context.scene.eswc_info.master_scene]

        # this is to avoid errors when changing percentage for preview render...
        context.scene.render.resolution_percentage = 100

        eswc_info = scn.eswc_info
        switch_screen(context, eswc_info.enum_edit_screen)
        context.screen.scene = scn

        return {'FINISHED'}

        # ---------------------------------------------------------------------


class S_CompOperator(bpy.types.Operator):
    bl_idname = "eswc.single_comp"
    bl_label = "Create Comp from strip"

    def copy_render_settings(self, scene_a, scene_b):
        '''
        Copy render settings for scene A to match original scene B
        '''
        scene_a.render.resolution_x = scene_b.render.resolution_x
        scene_a.render.resolution_y = scene_b.render.resolution_y
        scene_a.render.resolution_percentage = scene_b.render.resolution_percentage
        scene_a.render.fps = scene_b.render.fps
        path = bpy.path.abspath(os.path.join("//Comp", scene_a.name + "/" + scene_a.name))
        scene_a.render.filepath = bpy.path.relpath(path)

    def copy_comp_render_settings(self, scene_a, scene_b):
        # copy compositor render settings
        scene_a.node_tree.use_opencl = scene_b.node_tree.use_opencl
        scene_a.node_tree.two_pass = scene_b.node_tree.two_pass
        scene_a.node_tree.render_quality = scene_b.node_tree.render_quality
        scene_a.node_tree.edit_quality = scene_b.node_tree.edit_quality
        scene_a.node_tree.chunk_size = scene_b.node_tree.chunk_size

    def copy_all_settings(self, scene_a, scene_b):
        '''
        Copy all listed settings for scene strip A scene_a.node_tree.use_opencl
        to match original scene strip B
        '''
        # scene_a.use_translation =  scene_b.use_translation
        scene_a.use_reverse_frames = scene_b.use_reverse_frames
        scene_a.use_float = scene_b.use_float
        scene_a.use_flip_y = scene_b.use_flip_y
        scene_a.use_deinterlace = scene_b.use_deinterlace
        scene_a.use_default_fade = scene_b.use_default_fade
        scene_a.strobe = scene_b.strobe
        scene_a.speed_factor = scene_b.speed_factor
        scene_a.mute = scene_b.mute
        scene_a.lock = scene_b.lock
        scene_a.effect_fader = scene_b.effect_fader
        scene_a.color_saturation = scene_b.color_saturation
        scene_a.color_multiply = scene_b.color_multiply
        scene_a.blend_type = scene_b.blend_type
        scene_a.blend_alpha = scene_b.blend_alpha
        scene_a.use_flip_x = scene_b.use_flip_x

    def setup_proxy(self, strip, eswc_info, new_name):
        strip.use_proxy = True
        if (eswc_info.pq == "1"):
            strip.proxy.build_25 = True
        else:
            strip.proxy.build_25 = False
        if (eswc_info.pq == "2"):
            strip.proxy.build_50 = True
        else:
            strip.proxy.build_50 = False
        if (eswc_info.pq == "3"):
            strip.proxy.build_75 = True
        else:
            strip.proxy.build_75 = False
        if (eswc_info.pq == "4"):
            strip.proxy.build_100 = True
        else:
            strip.proxy.build_100 = False
        strip.use_proxy_custom_directory = True
        # blender file path
        file = bpy.data.filepath
        name = new_name
        proxy_folder = bpy.path.abspath("//.proxy")
        new_folder = os.path.join(proxy_folder, name)
        rel_folder = bpy.path.relpath(new_folder)
        strip.proxy.directory = rel_folder
        strip.proxy.quality = 90

    def create_composition_for_strip(self, original_strip, context):
        # Creates new scene but doesn't set it as active.
        new_scene_name = '{}{}'.format('Comp_', original_strip.name)
        new_scene = bpy.data.scenes.new(new_scene_name)

        current_scene = context.scene
        eswc_info = current_scene.eswc_info

        # set comp_name
        # TODO: Collection of string properties holding the strip names
        # TODO: give strip in timeline the name of the original movie strip?
        new_scene.eswc_info.comp_name = original_strip.name

        # Change render settings for new scene to match original scene
        self.copy_render_settings(new_scene, current_scene)

        # Setup new scene EndFrame to match original_strip length
        if not eswc_info.bool_preserve_duration:
            new_scene.frame_start = 1
            new_scene.frame_end = original_strip.frame_final_duration
        else:
            new_scene.frame_end = original_strip.frame_final_duration + original_strip.frame_offset_start + original_strip.frame_offset_end

        # Setup nodes
        new_scene.use_nodes = True

        self.create_node_tree_for_strip(new_scene, original_strip, eswc_info, context)

        # Create Marker that indicates the original_strip's length in the scene.
        # TODO: Update the marker positions on everytime the composition is opened.
        if eswc_info.bool_preserve_duration:
            bpy.ops.marker.add()
            playhead = context.scene.frame_current
            marker_offset = original_strip.frame_offset_start - playhead
            bpy.ops.marker.move(frames=marker_offset)
            bpy.ops.marker.make_links_scene(scene=new_scene.name)
            bpy.ops.marker.delete()

        context.screen.scene.update()

        # Add newly created scene to the timeline
        channel_increase = eswc_info.channel_increase
        if not eswc_info.bool_preserve_duration:
            bpy.ops.sequencer.scene_strip_add(
                frame_start=original_strip.frame_start,
                channel=original_strip.channel + channel_increase,
                replace_sel=False, scene=new_scene.name)
        else:
            bpy.ops.sequencer.scene_strip_add(
                frame_start=original_strip.frame_start,
                channel=original_strip.channel + channel_increase,
                replace_sel=False, scene=new_scene.name)

        # Copy Settings
        settings = eswc_info.settings

        # make new original_strip active
        context.scene.sequence_editor.active_strip = bpy.data.scenes[current_scene.name].sequence_editor. \
                sequences_all[new_scene.name]
        new_strip = context.scene.sequence_editor.active_strip

        # deselect all other strips
        for i in context.selected_editable_sequences:
            if i.name != new_strip.name:
                i.select = False

        # Update scene
        context.scene.update()

        # Camera override
        new_strip.scene_camera = current_scene.camera

        # Match the original clip's length
        if eswc_info.bool_preserve_duration == False:
            new_strip.frame_start = original_strip.frame_start + original_strip.frame_offset_start
            new_strip.frame_final_duration = original_strip.frame_final_duration
            new_strip.animation_offset_start = 0
            new_strip.animation_offset_end = 0
        else:
            triminout(new_strip,
                      original_strip.frame_start + original_strip.frame_offset_start,
                      original_strip.frame_start + original_strip.frame_offset_start + \
                      original_strip.frame_final_duration)

        context.scene.update()

        # Save the original_strip's master scene
        bpy.data.scenes[new_scene.name].eswc_info.master_scene = current_scene.name

        if (settings == "All"):
            a = bpy.data.scenes[current_scene.name].sequence_editor.sequences[new_scene.name]
            b = bpy.data.scenes[current_scene.name].sequence_editor.sequences_all[original_strip.name]
            self.copy_all_settings(a, b)

        if (eswc_info.bool_auto_proxy == True):
            a = bpy.data.scenes[current_scene.name].sequence_editor.sequences[new_scene.name]
            self.setup_proxy(a, eswc_info, new_scene.name)

    def create_node_tree_for_strip(self, new_scene, strip, eswc_info, context):
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
            filename = os.path.basename(strip_path)

            # Check for existing image datablocks for this item
            bool_create_new = True
            D = bpy.data
            # print(strip_path)
            for file in D.images:
                if file.filepath == strip_path:
                    strip_source = bpy.data.images[file.name]
                    bool_create_new = False
            # or create a new one
            if bool_create_new:
                strip_source = bpy.data.images.load(strip_path)
                strip_source.source = 'MOVIE'
            image_node.image = strip_source

        # Other input settings
        if eswc_info.bool_preserve_duration == False:
            image_node.frame_duration = strip.frame_final_duration
            image_node.frame_offset = strip.frame_offset_start + \
                              strip.animation_offset_start
        else:
            image_node.frame_duration = strip.frame_final_duration + \
                                strip.frame_offset_start + strip.frame_offset_end + \
                                strip.animation_offset_end
            image_node.frame_offset = strip.animation_offset_start

        image_node.use_cyclic = False
        image_node.use_auto_refresh = True

        # Update scene
        new_scene.update()
        # strip_source.update()
        new_scene.frame_current = 2

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
        scn = context.scene


            # Get selected strips, current scene, and

        # current camera, used for linking with other scenes
        selected_strips = context.selected_sequences
        current_scene = bpy.data.scenes[context.scene.name]
        current_camera = current_scene.camera

        # Loop selected strips                         
        for strip in selected_strips:

            # Check if strip is a movie
            if strip.type == 'MOVIE' or 'IMAGE':
                self.create_composition_for_strip(strip, context)

            else:
                print("Active Strip is not a movie or an image sequence.")

        return {'FINISHED'}


def register():
    bpy.utils.register_module(__name__)

    # eswc_info
    bpy.types.Scene.eswc_info = PointerProperty(type=ESWC_Info)

    # strip composite scene name; used to interchange movies and composites
    bpy.types.ImageSequence.CompositeScene = bpy.props.StringProperty(
        name="Composite Scene",
        description="The name of the composite scene associated to the strip",
        default=""
    )
    bpy.types.MovieSequence.CompositeScene = bpy.props.StringProperty(
        name="Composite Scene",
        description="The name of the composite scene associated to the strip",
        default=""
    )
    bpy.types.MovieClipSequence.CompositeScene = bpy.props.StringProperty(
        name="Composite Scene",
        description="The name of the composite scene associated to the strip",
        default=""
    )

def unregister():
    bpy.utils.unregister_module(__name__)

    # eswc_info
    del bpy.types.Scene.eswc_info


if __name__ == "__main__":
    register()
