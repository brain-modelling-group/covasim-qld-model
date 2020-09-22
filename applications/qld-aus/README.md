# Modelling COVID-19 in  Queensland Australia with covasim

The main QLD-specific code is in `covasim-australia/applications/qld-aus/`

## Usage

1. `export PYTHONPATH=/home/user/path/to/covasim-australia-qld:$PYTHONPATH`

2. ` cd applications/qld-aus/`

3. `python make_qld_pop.py` running this command will produce a file called `qldppl.pop`

4. `python run_qld_wave_01.py`, running this command will: launch 10 runs for three different values of global transmissibility.
                                                           create `results/` directory where results are stored in `.obj` files

5. create `figs` directory if it does not exist.

6. run  `python_qld_report_figure.py`