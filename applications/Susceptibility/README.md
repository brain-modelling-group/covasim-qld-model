# Outbreak probability analysis

The main code is in `covasim-australia/applications/Susceptibility/outbreak`

## Usage

1. Define policy packages to run in `outbreak/policy_packages.xlsx`
2. Run `run_susceptibility.py` to simulate. This file can be run in one of several ways
    - `python run_susceptibility.py` or with Pycharm. This will perform a default number of runs executing in 1 thread
    - `python run_susceptibility.py --nruns=1000` will do 1000 runs (same parameters/packages, different seeds)
    - `python run_susceptibility.py --celery=True` will use Celery workers for parallelization.
       To use Celery, run `./run_celery.sh` in a separate command window. `redis` will need to be running (already the 
       case on Athena and Apollo). This resolves an issue with `sc.parallelize` getting stuck with 1000+ runs
    
    By default, `run_susceptibility.py` will generate `{policy_name}.stats` files contained output values but not
    saved simulations. This is because writing all of the simulations to disk is extremely slow (slower than actually
    running them). 
3. Run `analyze_susceptibility.py` to load the `*.stats` files and generate output plots