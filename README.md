# Covasim Australia QLD

This reduced repo includes qld-specific agent-based model using covasim, 
and the minimal amount of data inherited from nsw and vic cases. 

# Installation 
1. Install Anaconda/Miniconda, or any other Python distro of choice.
2. Create a new environment to have all the covid related libraries (Python >= 3.6).
3. Activate your environment.
4. Go to directory `covasim-australia-qld/`
5. Run `pip install covasim`  -- this command installs covasim. Version used to develop and test is [covasim 1.7.6](https://github.com/InstituteforDiseaseModeling/covasim/releases/tag/v1.7.6).
6. Run `python setup.py install` -- this command installs the classed and funs in `covasim_australia/`
7. Set up `PYTHONPATH` as `export PYTHONPATH=/home/user/you/path/to/covasim-qld-model:$PYTHONPATH`

That's it. Scripts sould run now. 
