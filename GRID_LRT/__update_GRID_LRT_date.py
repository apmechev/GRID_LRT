import datetime
import GRID_LRT

def modify_updated_date(date = datetime.datetime.now().date()):
    mod_file = GRID_LRT.__file__.replace('pyc','py')
    with open(mod_file) as _file:
        file_data = _file.read()
    file_data = file_data.split('\n')
    for i in file_data: 
        if '__date__' in i:
            idx = file_data.index(i)
            file_data[idx] = "__date__ = \"%s\"" %(date.isoformat())
    with open(mod_file,'w') as _file:
        _file.write('\n'.join(file_data))

if __name__ == '__main__':
    modify_updated_date()
