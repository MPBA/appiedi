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
def generate_map(timestamp_start, timestamp_end, map_name, day=-1, default_val=None):
    nomeR = map_name + "_punti3"
    try:
        grass.run_command("v.db.connect", flags="d", map=nomeR, quiet=True)
        # grass.run_command("g.mremove", flags="fr", vect=map_name + "_*", rast=map_name + "_*", overwrite=True, quiet=True)
        grass.run_command("g.mremove",
                          flags="fr",
                          vect='{0}_*'.format(map_name),
                          rast="{0}_*".format(map_name),
                          overwrite=True,
                          quiet=True)
    except:
        pass

    grass.run_command("db.connect",
                      database="host={0},port={1},dbname={2},schema=public"
                               .format(HOSTDB, PORTDB, USERDB),
                      driver="pg",
                      quiet=True)

    grass.run_command("db.login", driver='pg', user=USERDB,
                      password=PASSWORDDB, quiet=True)

    grass.read_command("db.connect", flags="p")

    grass.run_command("g.region",
                      w='648315.280814473', s='5089928.11165279',
                      e='677478.656978493', n='5116773.10179288',
                      res='20')

    where = "mtl_timestamp > '{0}' and mtl_timestamp < '{1}'"\
            .format(timestamp_start, timestamp_end)

    if day >= 0:
        # where += " and extract(dow FROM mtl_timestamp)=" + str(day % 7)
        where += " and date_part('dow',mtl_timestamp)={0}".format((day % 7))

    grass.run_command("v.in.db",
                      flags="t", table="telecom_dataset_trento",
                      x="ST_X(the_geom)", y="ST_Y(the_geom)",
                      key="id", output=nomeR , where=where, overwrite=True)

    grass.run_command("v.surf.bspline",
                      input=nomeR, raster_output='{0}_rasterCo'.format(map_name),
                      method="linear", column="co", _lambda="0.05",
                      overwrite=True, quiet=True)

    grass.run_command("r.mapcalc",
                      expression="{0}_no0=if({0}_rasterCo,{0}_rasterCo,0,0)"
                                 .format(map_name),
                      overwrite=True, quiet=True)

    grass.run_command("r.mapcalc",
                      expression="{0}_co9999=if(isnull({0}_no0),-9999,{0}_no0)"
                                 .format(map_name),
                      overwrite=True, quiet=True)

    grass.run_command("r.out.gdal",
                      input="{0}_co9999".format(map_name), format="GTiff",
                      output="{0}{1}.tiff".format(DIRECTORY, map_name),
                      overwrite=True, quiet=True)

    if default_val is not None:
        grass.run_command("r.mapcalc",
                          expression="{0}_coavg=if(isnull({0}_no0),{1},{0}_no0)"
                                     .format(map_name, default_val),
                          overwrite=True, quiet=True)

        grass.run_command("r.out.gdal",
                          input="{0}_coavg".format(map_name), format="GTiff",
                          output='{0}{1}_avg.tiff'.format(DIRECTORY, map_name),
                          overwrite=True, quiet=True)

    # uploadRasterMap(DIRECTORY, nomeMappa + ".tiff")
    grass.run_command("v.db.connect",
                      flags="d", map=nomeR, quiet=True)

    grass.run_command("g.mremove",
                      flags="fr", vect="{0}_*".format(map_name),
                      rast="{0}_*".format(map_name), overwrite=True, quiet=True)
    return True


if __name__ == "__main__":
    inizio = "2013-12-10 00:00:00"
    fine = "2013-12-17 00:00:00"
    generate_map(inizio, fine, "lunedi", 2)
