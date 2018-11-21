import datetime

from GRID_LRT.storage.gsifile  import GSIFile

base_dir = 'gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/SKSP/pref_targ1/'
b_dir = GSIFile(base_dir)
files = b_dir.list_dir()

to_delete = []

for f in files:
    if f.datetime < datetime.datetime.now() - datetime.timedelta(days=31):
        to_delete.append(f)

for fi in to_delete:
    print fi.datetime

