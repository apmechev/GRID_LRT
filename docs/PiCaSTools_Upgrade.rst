.. GRID_LRT documentation master file, created by
   sphinx-quickstart on Mon Feb  5 09:40:38 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Upgrade of Grid_PiCaS_tools
====================================

It's finally time to upgrade the picas_tools backend to make it into a bonafide PiCaS_Launcher. There are a couple of changes in the new version of the framework:

1.  Change 

.. code:: bash

    python getSBX.py $1 $2 $3 $4& 


with 

.. code:: bash

    python Launch.py  $1 $2 $3 $4 &

into your run_remote_sandbox.sh (This is located in various locations but one good place to look for it is {GRID_LRT/Sandbox/Launchers} for the Old versions and {GRID_LRT/data/launchers} for versions >0.2.x)

2. Build your sandboxes with the new GRID_Sandbox repository (fork if you have to). This also requires the newest (>0.2) version of GRID_LRT. Building the SBX is easy. Use


.. code-block:: python 

    sbx=GRID_LRT.sandbox.Sandbox()
    sbx.build_sandbox('config_file_here') 
    sbx.upload_sandbox()


config files are in GRID_LRT/data/config. modify as you wish.

3. Modifying Sandbox: 

   The location of all the sandbox files are no longer inside the GRID_LRT repository, but in my GRID_Sandbox repo. Each sandbox is a different branch. you can fork it to make your own SBX if you want, just change the url in your config files. 

4. Not worrying: 

   Your files will automatically download and extract by default into the ${RUNDIR}/Input directory. This works for most of the LTA data, unless there's some funky monkey thing going on with the filenames. If so, you can write your own download script rather than relying on generic download (the fallback method located in GRID_PiCaS_Launcher/bin) 
