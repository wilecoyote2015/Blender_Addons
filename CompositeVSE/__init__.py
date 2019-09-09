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

from CompositeVSE.handlers_high_bit_depth import register_handlers, unregister_handlers
from CompositeVSE.operator_composition import OperatorCreateCompositionFromStrip
from CompositeVSE.operators_navigation import (
    Switch_back_to_Timeline_Operator,
    Switch_to_Composite_Nodepanel_Operator,
    Switch_to_Composite_Operator
)
from CompositeVSE.ui_panels import CompPanel, NodePanel
from CompositeVSE.eswc_info import ESWC_Info

import bpy

# todo: also handle clips in metastrips for creating strip from composition if metastrip contains sound, corresponding
#  video only

bl_info = {
    "name": "Edit Strip With Compositor",
    "description": "Send one or more Sequencer strips to the Compositor, gently",
    "author": "Carlos Padial, TMW, Björn Sonnenschein",
    "version": (0, 15),
    "blender": (2, 80, 0),
    "location": "Sequencer > UI panel, Node Editor > UI panel",
    "wiki_url": "None Yet"
                "None Yet",
    "tracker_url": "None"
                   "func=detail&aid=<number>",
    "category": "Sequencer"
}

classes = (
    ESWC_Info,
    CompPanel,
    NodePanel,
    Switch_to_Composite_Operator,
    Switch_to_Composite_Nodepanel_Operator,
    Switch_back_to_Timeline_Operator,
    OperatorCreateCompositionFromStrip
)

register_classes, unregister_classes = bpy.utils.register_classes_factory(classes)

def register():
    print('Registered VSE Compositor addon')
    register_classes()
    bpy.types.Scene.eswc_info = bpy.props.PointerProperty(type=ESWC_Info)
    register_handlers()
    
    ### Props for identification of scenes belonging to strips
    # strip composite scene name; used to interchange movies and composites
    
    # todo: rename the properties to start with eswc.
    bpy.types.ImageSequence.composite_scene = bpy.props.StringProperty(
        name="Composite Scene",
        description="The name of the composite scene associated to the strip",
        default=""
    )
    bpy.types.MovieSequence.composite_scene = bpy.props.StringProperty(
        name="Composite Scene",
        description="The name of the composite scene associated to the strip",
        default=""
    )
    # todo: MovieClip sequences are not supported yet.
    bpy.types.MovieClipSequence.composite_scene = bpy.props.StringProperty(
        name="Composite Scene",
        description="The name of the composite scene associated to the strip",
        default=""
    )


def unregister():
    unregister_classes()
    unregister_handlers()
    del bpy.types.Scene.eswc_info
    del bpy.types.MovieClipSequence.composite_scene
    del bpy.types.MovieSequence.composite_scene
    del bpy.types.ImageSequence.composite_scene

if __name__ == "__main__":
    register()
