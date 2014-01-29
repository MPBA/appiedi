import os
import sys
from local_settings import DB_SETTINGS

HOSTDB = DB_SETTINGS['host']
PORTDB = DB_SETTINGS['port']
USERDB = DB_SETTINGS['user']
PASSWORDDB = DB_SETTINGS['password']
DIRECTORY = "/hardmnt/geopg0/db93stable/appiedi/grass_output/"

# init grass
gisbase = os.environ['GISBASE'] = "/usr/local/share/grass/grass-7.0.svn"
gisdbase = "/hardmnt/geopg0/db93stable/appiedi/grass"
location = "location"
mapset = "PERMANENT"
sys.path.append(os.path.join(os.environ['GISBASE'], "etc", "python"))

import grass.script as grass
import grass.script.setup as gsetup

gsetup.init(gisbase, gisdbase, location, mapset)

print grass.gisenv()


#inizio: data inizio es "2013-12-10 00:00:00"
#file: data fine es
#nome mappa  "2013-12-17 00:00:00"
#0 domenica,1 lunedi,2 domencica

# script di enrico
def generate_map(timestamp_start, timestamp_end, map_name, day=-1):
    nomeR = map_name + "_punti3"
    try:
        grass.run_command("v.db.connect", flags="d", map=nomeR, quiet=True)
        grass.run_command("g.mremove", flags="fr", vect=map_name + "_*", rast=map_name + "_*", overwrite=True, quiet=True)
    except:
        pass

    # gsetup.init(os.getenv('GISBASE'), GRASSLOCATION, "TRento", MAPSET)
    grass.run_command("db.connect", database="host=" + HOSTDB + ",port=" + PORTDB + ",dbname=" + USERDB + ",schema=public", driver="pg" , quiet=True)
    grass.run_command("db.login", driver='pg', user=USERDB, password=PASSWORDDB, quiet=True)
    grass.read_command("db.connect", flags="p")
    # grass.run_command("g.region" , res=20)
    grass.run_command("g.region", w='648315.280814473', s='5089928.11165279', e='677478.656978493', n='5116773.10179288', res='20')
    where = "mtl_timestamp > '{0}' and mtl_timestamp < '{1}'".format(timestamp_start, timestamp_end)
    # "mtl_timestamp > '2013-01-12 00:00:00' and mtl_timestamp < '2013-01-19 00:00:00'"
    if day >= 0:
        # where += " and extract(dow FROM mtl_timestamp)=" + str(day % 7)
        where += " and date_part('dow',mtl_timestamp)=" + str(day % 7)
    grass.run_command("v.in.db", flags="t", table="telecom_dataset_trento", x="ST_X(the_geom)", y="ST_Y(the_geom)", key="id",
                      output=nomeR , where=where
                      , overwrite=True)
    # grass.run_command("g.region", vect=nomeR, res=20)
    grass.run_command("v.surf.bspline", input=nomeR , raster_output=map_name + "_rasterCo", method="linear", column="co", _lambda="0.05", overwrite=True, quiet=False)

    grass.run_command("r.mapcalc", expression=map_name + "_no0=if(" + map_name + "_rasterCo," + map_name + "_rasterCo,0,0)", overwrite=True, quiet=True)
    grass.run_command("r.mapcalc", expression=map_name + "_co9999=if(isnull(" + map_name + "_no0),-9999," + map_name + "_no0)", overwrite=True, quiet=True)
    grass.run_command("r.out.gdal", input=map_name + "_co9999", format="GTiff", output=DIRECTORY + map_name + ".tiff", overwrite=True, quiet=True);
    # uploadRasterMap(DIRECTORY, nomeMappa + ".tiff")
    grass.run_command("v.db.connect", flags="d", map=nomeR, quiet=True)
    grass.run_command("g.mremove", flags="fr", vect=map_name + "_*", rast=map_name + "_*", overwrite=True, quiet=True)
    return True


if __name__ == "__main__":
    inizio = "2013-12-10 00:00:00"
    fine = "2013-12-17 00:00:00"
    generate_map(inizio, fine, "lunedi", 2)
