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

from CompositeVSE.common_functions import toggle_composition_visibility

from bpy.props import (IntProperty,
                       FloatProperty,
                       EnumProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty,
                       PointerProperty,
                       )
import bpy
 
class ESWC_Info(bpy.types.PropertyGroup):
    bool_show_options: BoolProperty(
        name="Show options",
        description="Show options",
        default=False)

    bool_add_scale: BoolProperty(
        name="Add Scale node",
        description="Add Scale node",
        default=False)

    # todo: implement update function
    bool_show_compositions: BoolProperty(
        name="Show composite strips",
        description="If activated, the composite are shown in the timeline. Otherwise, the source videos are visible.",
        default=True,
        update=toggle_composition_visibility)

    bool_reuse_compositions: BoolProperty(
        name="Reuse compositions",
        description="When creating compositions for strips, reuse existing compositions that use the same source",
        default=True)

    bool_add_viewer: BoolProperty(
        name="Add Viewer",
        description="You can add a viewer node to the new compositions \
        automatically",
        default=True)

    bool_use_high_bit_depth_fix: BoolProperty(
        name="Use High Bitdepth Fix",
        description="Workaround for 10 Bit videos in compositor while rendering",
        default=True)

    bool_add_group: BoolProperty(
        name="Add Nodegroup",
        description="You can add a custom node group to the new compositions \
        automatically",
        default=False)

    # the input path of the movie file the composition was created from
    # if it is empty, the operators infer that the current scene
    # is not a composition.
    path_input: StringProperty(
        name="Movie strip input",
        default="",
        description="the input path of the movie file the composition was \
            created from")

    # store original strip type so that a strip can be created from the composition
    type_original_strip: StringProperty(
        name="Original strip type",
        default="",
        description="Type of the strip associated with this composition")

    selections = [("All", "All", "Copy all settings"),
                  # ( "Select", "Select", "Copy selected settings" ),
                  ("None", "None", "Copy none of the settings")]
    settings: EnumProperty(
        name="Settings Type",
        items=selections,
        default="All",
        description="Choose which settings to copy from the source clip to the created composition")

    master_scene: StringProperty(
        name="Master Scene",
        description="This is the name of the Scene's Master Scene",
        default="Scene")

    scene_init_comp: BoolProperty(name="",
                                   description="",
                                   default=False)

    def avail_nodegroups(self, context):
        items = []
        for i, node_group in enumerate(bpy.data.node_groups):
            items.append((str(i), node_group.name, node_group.name))
        return items

    enum_node_groups: EnumProperty(items=avail_nodegroups,
                                    name="Node Group")



    # TODO: Default to Composite workspace and workspace used for editing when switched the first time.
    # enum_edit_screen: EnumProperty(items=avail_screens,
    #                                 name="Editing Workspace")

    edit_screen: StringProperty(
        name='Editing Workspace',
        default=''
    )
    comp_screen: StringProperty(
        name='Compositing Workspace',
        default=''
    )

    # enum_comp_screen: EnumProperty(items=avail_screens,
    #                                 name="Compositing Workspace")

