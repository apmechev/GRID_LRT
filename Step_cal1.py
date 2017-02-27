#!/bin/env python 

import class_srmlist


def stage(srmlist):
    import class_srmlist
    s=class_srmlist.Srm_manager(stride=1)
    s.file_load(srmlist)
    _=s.state()
    d=s.make_sbndict_from_file(srmlist)

def make_tokens():
    pass
