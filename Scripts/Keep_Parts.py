#==================================
#Author Bjorn Burr Nyberg 
#University of Bergen
#Contact bjorn.nyberg@uni.no
#Copyright 2013
#==================================

'''This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.'''

#==================================

#Definition of inputs and outputs
#==================================
##[SAFARI]=group
##Polygon=vector
##Area_Threshold=number 0
##Output=output vector

#Algorithm body
#==================================
#TODO add multipolygon support/multipart/singlepart support

from qgis.core import *
from PyQt4.QtCore import *
from itertools import chain
import networkx as nx
import sextante as st

layer = st.getobject(Polygon)

fields= layer.pendingFields()
crs = layer.crs()

writer = QgsVectorFileWriter(Output, "CP1250", fields, 3,layer.crs(), "ESRI Shapefile")
fet = QgsFeature(fields)
Total = layer.featureCount()
progress.setText('Extracting Parts')
for enum,feature in enumerate(layer.getFeatures()):
    progress.setPercentage(int((100 * enum)/Total))
    geom = feature.geometry().asPolygon()
    for part in geom[1:]:
        geom = [[QgsPoint(pnt.x(),pnt.y()) for pnt in part]]
        polygon = QgsGeometry.fromPolygon(geom)
        for field in fields:
            fet[field.name()] = feature[field.name()]
        fet.setGeometry(polygon)
        writer.addFeature(fet)

del writer
layer = st.getobject(Output)
layer.startEditing()
if Area_Threshold != 0: 
    progress.setText('Updating Features')
    for enum,feature in enumerate(layer.getFeatures()):
        progress.setPercentage(int((100 * enum)/Total))
        if feature.geometry().area() < Area_Threshold:
            layer.deleteFeature(feature.id())
layer.commitChanges()
        