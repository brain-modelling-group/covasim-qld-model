# Covasim Australia QLD

This branch `qld-resurgence` is based on optima/covasim-australia repository, branch `vic-resurgence`, BUT importantly it includes the first qld-specific model developed in branch `qld-calibration`. Note that this branch `qld-resurgence` is the default branch of `covasim-australia-qld` -- usually called `master`in many projects. 

The main differences of this branch in comparison to the now deprecated `qld-calibration` branch is the folder `covasim_australia/`, which includes all the classes and functions that used to be at the top level of `covasim-australia-qld`. This folder now behaves as a standalone module, thus simplifying function imports and relative/absolute path issues we had encountered before.  branch 

Branch `qld-resurgence` originated on 2020-09-17. 

# Installation 
1. Install Anaconda/Miniconda, or any other Python distro of choice.
2. Create a new environment to have all the covid related libraries (Python >= 3.6).
3. Activate your environment.
4. Go to directory `covasim-australia-qld/`
5. Run `pip install covasim`  -- this command installs covasim: https://github.com/institutefordiseasemodeling/covasim
6. Run `python setup.py install` -- this command installs the classed and funs in `covasim_australia/`
7. Set up `PYTHONPATH` as `export PYTHONPATH=/home/user/you/path/to/covasim-australia-qld:$PYTHONPATH`

That's it. Scripts sould run now. 
