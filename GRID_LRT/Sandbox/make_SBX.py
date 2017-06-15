#!/bin/env python
import sandbox
s=sandbox.Sandbox()
s.parseconfig('prefactor_cal1.yml')
s.create_SBX_folder()
s.enter_SBX_folder()
s.load_git_scripts()
s.copy_base_scripts()
s.check_token('/home/apmechev/GRID_LRT/config/tokens/pref_cal2_token.cfg')
s.zip_SBX()
s.upload_SBX()
s.cleanup()


