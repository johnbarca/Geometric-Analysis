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
##Voronoi_Lines=vector
##Loops=number 1
##Groupby_Field=field Voronoi_Lines
##Output=output vector

#Algorithm body
#==================================
import networkx as nx
import sextante as st
from qgis.core import *
from PyQt4.QtCore import QVariant

layer = st.getobject(Voronoi_Lines)

Total = layer.featureCount()
edges = {}
progress.setText('Calculating Edges')
for enum,feature in enumerate(layer.getFeatures()):
    try:
        progress.setPercentage(int((100 * enum)/Total))
        points = feature.geometry().asPolyline()
        pnts1 = (float(points[0][0]),float(points[0][1]))
        pnts2 = (float(points[1][0]),float(points[1][1]))
        Length = feature.geometry().length()
        ID = feature[Groupby_Field]
        if ID in edges:
            edges[ID].append((pnts1,pnts2,Length))
        else:
            edges[ID] = [(pnts1,pnts2,Length)]
    except Exception:
        continue ##Possible Collapsed Polyline?

fields = QgsFields()
fields.append( QgsField('FID', QVariant.Int ))
fet = QgsFeature(fields)

writer = QgsVectorFileWriter(Output, "CP1250", fields, layer.dataProvider().geometryType(),layer.crs(), "ESRI Shapefile")

progress.setText('Triming Lines')
G = nx.Graph()
Total2 = len(edges)
data = set([])
for enum,FID in enumerate(edges):
    progress.setPercentage(int((100 * enum)/Total2))
    G.add_weighted_edges_from(edges[FID])
    for n in range(Loops):
        degree = G.degree()
        keepNodes = [k for k,v in degree.iteritems() if v == 1]
        G.remove_nodes_from(keepNodes)
    data.update(G.nodes())  
    
    G.clear()

progress.setText('Creating Segments')
for enum,feature in enumerate(layer.getFeatures()):
    progress.setPercentage(int((100 * enum)/Total))
    points = feature.geometry().asPolyline()
    if len(points) != 2: #Possible Collapsed Polyline?
        continue
    pnts1 = (float(points[0][0]),float(points[0][1]))
    pnts2 = (float(points[1][0]),float(points[1][1]))
    if pnts1 in data and pnts2 in data:
        points = [QgsPoint(pnts1[0],pnts1[1]),QgsPoint(pnts2[0],pnts2[1])]
        fet.setGeometry(QgsGeometry.fromPolyline(points))
        fet[0] = feature[Groupby_Field]
        writer.addFeature(fet)

del writer