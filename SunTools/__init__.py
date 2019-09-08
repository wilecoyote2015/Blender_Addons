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
    PanelTrimTools
)
from SunTools.scene_types import SunToolsInfo

bl_info = {
    "name": "SunTools",
    "description": "Define in- and outpoints of your material in the file browser",
    "author": "Björn Sonnenschein",
    "version": (1, 3),
    "blender": (2, 80, 0),
    "location": "File Browser > Tools",
    "wiki_url": "None Yet"
                "None Yet",
    "tracker_url": "None"
                   "func=detail&aid=<number>",
    "category": "Sequencer"}

classes = (
    SunToolsInfo,
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
    PanelTrimTools
)

register_classes, unregister_classes = bpy.utils.register_classes_factory(classes)

def register():
    register_classes()
    bpy.types.Scene.suntools_info = bpy.props.PointerProperty(type=SunToolsInfo)

def unregister():
    unregister_classes()
    del bpy.types.Scene.suntools_info

if __name__ == "__main__":
    register()

