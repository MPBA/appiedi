import sys
from osgeo import ogr
from findpath_edges import findpath
from dijkstra import dijkstra
from local_settings import DB_SETTINGS

conn = ogr.Open(
    'PG:dbname={0} host={1} port={2} user={3} password={4}'
    .format(DB_SETTINGS['database'], DB_SETTINGS['host'], DB_SETTINGS['port'],
            DB_SETTINGS['user'], DB_SETTINGS['password'])
)

# ds = ogr.Open("grafo_random.shp")
if conn is None:
    print "Open failed.\n"
    sys.exit(1)

lyr = conn.GetLayer('grafo_trento')

lyr.ResetReading()

linesList = []

edges = []

for feat in lyr:
    linesList.append(feat)
    edges.append([feat['length'], feat['co'], []])

for i in range(0, len(linesList)):
    geom0 = linesList[i].GetGeometryRef()
    start0x = geom0.GetX(0)
    start0y = geom0.GetY(0)
    end0x = geom0.GetX(geom0.GetPointCount() - 1)
    end0y = geom0.GetY(geom0.GetPointCount() - 1)
    for j in range(i + 1, len(linesList)):
        geom1 = linesList[j].GetGeometryRef()
        start1x = geom1.GetX(0)
        start1y = geom1.GetY(0)
        end1x = geom1.GetX(geom1.GetPointCount() - 1)
        end1y = geom1.GetY(geom1.GetPointCount() - 1)
        if ((start0x == start1x and start0y == start1y) or (
                start0x == end1x and start0y == end1y) or (
                end0x == start1x and end0y == start1y) or (
                end0x == end1x and end0y == end1y)):
            edges[i][2].append(j)
            edges[j][2].append(i)

# here function findpath should be called

ds = None
