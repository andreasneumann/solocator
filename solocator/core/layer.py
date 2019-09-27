# -*- coding: utf-8 -*-
"""
/***************************************************************************

 QGIS Solothurn Locator Plugin
 Copyright (C) 2019 Denis Rouzaud

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""


from copy import deepcopy

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QTreeWidgetItem

from qgis.core import QgsRasterLayer, QgsProject


# Compatibility for QGIS < 3.10
# TODO: remove
try:
    from qgis.gui.QgsLayerTreeRegistryBridge import InsertionPoint
except ModuleNotFoundError:
    from .qgs_layer_tree_insertion_point import InsertionPoint, layerTreeInsertionPoint


class SoLayer:
    def __init__(self, name: str, crs: str, wms_datasource: dict, postgis_datasource: dict, description: str):
        self.name = name
        self.crs = crs
        self.description = description
        # fix for wms_datasource
        if type(wms_datasource) is list and len(wms_datasource) == 1:
            wms_datasource = wms_datasource[0]
        self.wms_datasource = wms_datasource
        self.postgis_datasource = postgis_datasource

    def __repr__(self):
        return 'SoLayer: {}'.format(self.name)

    def load(self, insertion_point: InsertionPoint):
        """
        Loads layer in the layer tree
        :param insertion_point: The insertion point in the layer tree (group + position)
        """
        url = "contextualWMSLegend=0&" \
              "crs={crs}&" \
              "dpiMode=7&" \
              "featureCount=10&" \
              "format=image/png&" \
              "layers={layer}&" \
              "styles&" \
              "url={url}".format(
            crs=self.crs, layer=self.wms_datasource['name'], url=self.wms_datasource['service_url']
        )
        layer = QgsRasterLayer(url, self.name, 'wms')
        QgsProject.instance().addMapLayer(layer, False)
        if insertion_point.position >= 0:
            insertion_point.group.insertLayer(insertion_point.position, layer)
        else:
            insertion_point.group.addLayer(layer)

    def tree_widget_item(self):
        item = QTreeWidgetItem([self.name])
        item.setData(0, Qt.UserRole, deepcopy(self))
        return item


class SoGroup:
    def __init__(self, name, children):
        self.name = name
        self.children = children

    def __repr__(self):
        return 'SoGroup: {} ( {} )'.format(self.name, ','.join([child.__repr__() for child in self.children]))

    def load(self, insertion_point: InsertionPoint):
        """
        Loads group in the layer tree
        :param insertion_point: The insertion point in the layer tree (group + position)
        """
        if insertion_point.position >= 0:
            group = insertion_point.group.insertGroup(insertion_point.position, self.name)
        else:
            group = insertion_point.group.addGroup(self.name)
        for i, child in enumerate(self.children):
            child.load(InsertionPoint(group, i))

    def tree_widget_item(self):
        item = QTreeWidgetItem([self.name])
        item.addChildren([child.tree_widget_item() for child in self.children])
        item.setData(0, Qt.UserRole, deepcopy(self))
        return item
