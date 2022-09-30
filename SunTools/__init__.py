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

from SunTools.operators_edit_range import (
    OperatorEditRange,
    OperatorBackToTimeline,
    OperatorInsertStripIntoMasterscene
)
from SunTools.operators_movie_manager import (
    OperatorSetTimeline,
    # OperatorHideSequences,
    OperatorCreateProxies,
    OperatorUnmeta
)
from SunTools.operators_trim_tools import (
    OperatorSelectCurrent,
    OperatorCutCurrent,
    OperatorTrimLeft,
    OperatorTrimRight,
    OperatorSnapEnd
)
from SunTools.ui_panels import (
    PanelMovieManagerBrowser,
    PanelMovieManager,
    PanelTrimTools,
    NodePanel,
    CompPanel,
    PanelDarktable
)
from SunTools.handlers_high_bit_depth import register_handlers, unregister_handlers
from SunTools.operator_composition import OperatorCreateCompositionFromStrip
from SunTools.operators_navigation import (
    Switch_back_to_Timeline_Operator,
    Switch_to_Composite_Nodepanel_Operator,
    Switch_to_Composite_Operator
)
from SunTools.operators_darktable import (
    OperatorOpenDarktable,
    OperatorCopyDarktableStyle,
    OperatorLoadXmpDarktable,
    OperatorSaveXmpDarktable,
)
from SunTools.scene_types import SunToolsInfo, ESWC_Info

bl_info = {
    "name": "SunTools",
    "description": "Define in- and outpoints of your material in the file browser",
    "author": "Carlos Padial, TMW, Björn Sonnenschein",
    "version": (1, 4),
    "blender": (3, 3, 0),
    "location": "File Browser > Tools, Sequencer > UI panel, Node Editor > UI panel",
    "wiki_url": "None Yet"
                "None Yet",
    "tracker_url": "None"
                   "func=detail&aid=<number>",
    "category": "Sequencer"}

classes = (
    SunToolsInfo,
    ESWC_Info,
    OperatorEditRange,
    OperatorBackToTimeline,
    OperatorInsertStripIntoMasterscene,
    OperatorSetTimeline,
    # OperatorHideSequences,
    OperatorCreateProxies,
    OperatorUnmeta,
    OperatorSelectCurrent,
    OperatorCutCurrent,
    OperatorTrimLeft,
    OperatorTrimRight,
    OperatorSnapEnd,
    PanelMovieManagerBrowser,
    PanelMovieManager,
    PanelTrimTools,
    PanelDarktable,
    CompPanel,
    NodePanel,
    Switch_to_Composite_Operator,
    Switch_to_Composite_Nodepanel_Operator,
    Switch_back_to_Timeline_Operator,
    OperatorCreateCompositionFromStrip,
    OperatorOpenDarktable,
    OperatorLoadXmpDarktable,
    OperatorSaveXmpDarktable,
    OperatorCopyDarktableStyle
)

register_classes, unregister_classes = bpy.utils.register_classes_factory(classes)

def register():
    bpy.types.MetaSequence.is_composite = bpy.props.BoolProperty(
        name='Is Composite',
        description='Whether the Meta Strip corresponds to Node Composition',
        default=False
    )
    bpy.types.MovieSequence.use_darktable = bpy.props.BoolProperty(
        name='Use Darktable for Strip',
        description='Use Darktable for color correction',
        default=False
    )
    bpy.types.MovieSequence.xmp_darktable = bpy.props.StringProperty(
        name='Darktable XMP',
        description='Parsed Darktable XMP',
        default=''
    )
    bpy.types.MovieSequence.source_darktable = bpy.props.StringProperty(
        name='Source',
        description='Source of Strip. Only used temporarily during render.',
        default=''
    )
    bpy.types.MovieSequence.frame_final_start_darktable = bpy.props.IntProperty(
        name='Frame Final Start',
        default=0
    )
    bpy.types.MovieSequence.frame_final_end_darktable = bpy.props.IntProperty(
        name='Frame Final End',
        default=0
    )
    bpy.types.MovieSequence.frame_offset_start_darktable = bpy.props.FloatProperty(
        name='Frame Offset Start',
        default=0
    )

    bpy.types.MovieSequence.frame_final_start_darktable_set = bpy.props.BoolProperty(
        name='Frame Final Start Set',
        default=False
    )
    bpy.types.MovieSequence.frame_final_end_darktable_set = bpy.props.BoolProperty(
        name='Frame Final End Set',
        default=False
    )
    bpy.types.MovieSequence.frame_offset_start_darktable_set = bpy.props.BoolProperty(
        name='Frame Offset Start Set',
        default=False
    )

    register_classes()
    bpy.types.Scene.suntools_info = bpy.props.PointerProperty(type=SunToolsInfo)
    bpy.types.Scene.eswc_info = bpy.props.PointerProperty(type=ESWC_Info)
    register_handlers()


def unregister():
    unregister_classes()
    unregister_handlers()

    del bpy.types.Scene.suntools_info
    del bpy.types.Scene.eswc_info
    # del bpy.types.MovieClipSequence.composite_scene
    del bpy.types.MetaSequence.is_composite

if __name__ == "__main__":
    register()

