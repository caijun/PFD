# -*- coding: utf-8 -*-
#===============================================================================
#        Scrape railway data from OpenStreetMap and convert to shapefile
#
#                       Version: 1.0.0 (2014-04-08)
#                         Interpreter: Python 2.7
#                        Test platform: Windows 7
#
#                    Author: Tony Tsai, Ph.D. Student
#          (Center for Earth System Science, Tsinghua University)
#               Contact Email: cai-j12@mails.tsinghua.edu.cn
#
#                    Copyright: belongs to Dr.Xu's Lab
#               (School of Environment, Tsinghua University)
# (College of Global Change and Earth System Science, Beijing Normal University)
#===============================================================================
from osmapi import OsmApi
import arcpy, os
from arcpy import env
from collections import OrderedDict

env.overwriteOutput = True
env.workspace = 'K:/Data/Admin/shp/network'

outdir = env.workspace + os.altsep + 'OSM'
if not os.path.exists(outdir):
    os.makedirs(outdir)

arcpy.CreateFeatureclass_management(outdir, "station.shp", "POINT", "", "DISABLED", "DISABLED", 
                                    "railway_station.shp")
station = outdir + os.altsep + 'station.shp'
# add fields to station
fields = ['nodeID', 'role', 'type', 'lon', 'lat', 'name_en', 'name_cn', 'relationID']
for field in fields:
    arcpy.AddField_management(station, field, "TEXT", "", "", 25)

arcpy.CreateFeatureclass_management(outdir, "railway.shp", "POLYLINE", "", "DISABLED", "DISABLED", 
                                    "railway_station.shp")
railway = outdir + os.altsep + 'railway.shp'
# add fields to railway
fields = ['wayID', 'type', 'source', 'usage', 'highspeed', 'maxspeed', 'gauge', 'relationID']
for field in fields:
    arcpy.AddField_management(railway, field, "TEXT", "", "", 25)

arcpy.CreateTable_management(outdir, "route_attr.dbf", "")
route = outdir + os.altsep + 'route.shp'
route_attr = outdir + os.altsep + 'route_attr.dbf'
# add fields to route_attr
arcpy.AddField_management(route_attr, "relationID", "TEXT", "", "", 25)
arcpy.AddField_management(route_attr, "type", "TEXT", "", "", 25)
arcpy.AddField_management(route_attr, "name_en", "TEXT", "", "", 25)
arcpy.AddField_management(route_attr, "name_cn", "TEXT", "", "", 25)
arcpy.AddField_management(route_attr, "descrip", "TEXT", "", "", 100)

osm = OsmApi()
    
def node2shp(nodeID):
    nodeData = osm.NodeGet(nodeID)
    print nodeData
    # open an insert cursor for the new feature class
    cur = arcpy.da.InsertCursor(station, ["SHAPE@XY", "nodeID", "lon", "lat", "name_en", "name_cn"])
    row = ((nodeData['lon'], nodeData['lat']), str(nodeData['id']), nodeData['lon'], nodeData['lat'], 
           nodeData['tag'].get('name:en', ''), nodeData['tag'].get('name:zh', nodeData['tag'].get('name', '')))
    cur.insertRow(row)
    del cur
    
def way2shp(wayID):
    wayData = osm.WayGet(wayID)
    print wayData
    # open an insert cursor for railway
    cur = arcpy.da.InsertCursor(railway, ["SHAPE@", "wayID", "source", "usage", "highspeed", "maxspeed", "gauge"])
    array = arcpy.Array()
    nd = wayData['nd']
    for n in nd:
        nodeData = osm.NodeGet(n)
        print nodeData
        array.append(arcpy.Point(nodeData['lon'], nodeData['lat']))
    row = [arcpy.Polyline(array), str(wayData['id']), wayData['tag'].get('source', ''), wayData['tag'].get('usage', ''), 
           wayData['tag'].get('highspeed', ''), wayData['tag'].get('maxspeed', ''), wayData['tag'].get('gauge', '')]
    cur.insertRow(row)
    del cur
    
def relation2shp(relationID):
    relationData = osm.RelationGet(relationID)
    print relationData
    memberData = relationData['member']
    for m in memberData:
        if m['type'] == 'node':
            node2shp(m['ref'])
            # update role, type and relationID fields for station
            cur = arcpy.UpdateCursor(station)
            for r in cur:
                if r.nodeID == str(m['ref']):
                    r.role = m['role']
                    r.type = m['type']
                    r.relationID = str(relationData['id'])
                    cur.updateRow(r)
            # delete cursor and row objects to remove locks on station 
            del r
            del cur
        elif m['type'] == 'way':
            way2shp(m['ref'])
            # update relationID field for railway
            cur = arcpy.UpdateCursor(railway)
            for r in cur:
                if r.wayID == str(m['ref']):
                    r.type = m['type']
                    r.relationID = str(relationData['id'])
                    cur.updateRow(r)
            # delete cursor and row objects to remove locks on station 
            del r
            del cur
    # open an insert cursor for route_attr
    cur = arcpy.da.InsertCursor(route_attr, ["relationID", "type", "name_en", "name_cn", "descrip"])
    row = [str(relationData['id']), relationData['tag'].get('type', ''), relationData['tag'].get('name:en', ''), 
           relationData['tag'].get('name:zh', relationData['tag'].get('name', '')), relationData['tag'].get('description', '')]
    cur.insertRow(row)
    del cur 

relations = OrderedDict([('甬台温铁路', 417230), ('温福铁路', 408506), ('福厦铁路', 408141), 
                          ('洛湛铁路', 3150028), ('宁西铁路', [3150028, 2047795]), ('宁启铁路', 2073769), 
                          ('铜九铁路', 2047712)])
for relationID in relations.values():
    if type(relationID) == type(list()):
        for rid in relationID:
            relation2shp(rid)
    else:
        relation2shp(relationID)

arcpy.Dissolve_management(railway, route, ["relationID"], "", "MULTI_PART", "DISSOLVE_LINES")
arcpy.JoinField_management(route, 'relationID', route_attr, 'relationID', ['type', 'name_en', 'name_cn', 'descrip'])
arcpy.DeleteField_management(station, ['Id'])
arcpy.DeleteField_management(route_attr, ['Field1'])