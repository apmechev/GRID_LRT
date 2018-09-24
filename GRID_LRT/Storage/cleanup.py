import datetime
from GRID_LRT.Storage.utils  import GSIFile



to_delete = []

def get_files_in_dir(base_dir='gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/SKSP/pref_targ1/'):
    b_dir = GSIFile(base_dir)
    files = b_dir.list_dir()
    return files

def list_files_older_than(files, num_days=31):
    to_delete = []
    for f in files:
        if f.datetime < datetime.datetime.now() - datetime.timedelta(days=num_days):
            to_delete.append(f)
    return to_delete

def text_format(fileobj):
    if fileobj.is_file:
        preamble = "File {}".format(fileobj.filename)
    else:
        preamble = "Folder {} with {} Files".format(fileobj.filename, fileobj._get_num_files())
    text = "{} modified on {} will be deleted. ".format(preamble, fileobj.datetime.strftime("%Y-%m-%d"))
    return text


def print_message_for_folder(base_dir, numdays, message=None, **kwargs):
    files = get_files_in_dir(base_dir)
    todeletefiles = list_files_older_than(files, num_days=numdays)
    if not message:
        print("Here are all the files I'll delete on Monday")
    else:
        print(message)
    print("for folder {}".format(base_dir))
    for f in todeletefiles:
        print(text_format(f))

def cleanup_folder(base_dir, numdays):
    print_message_for_folder(base_dir, numdays, message="Deleting these files!")
    files = get_files_in_dir(base_dir)
    todeletefiles = list_files_older_than(files, num_days=numdays)
    for f in todeletefiles:
        if f.is_dir:
            for subdir in f.list_dir():
                subdir.delete()
            f.delete()
        else:
            f.remove()
