# Victoria calibration

The main script to use for calibration is `vic_calibrate.py`.

# Resurgence analysis

The resurgence analysis consists of two parts

1. Finding seeds and beta values to use for the projections ('calibration')
2. Running the projections ('projection')

# Celery architecture

- Celery workers are started using `resurgence/celery.py`
- `resurgence/main.py` implements functions to load parameters and construct `Sim` instances
- `resurgence/celery.py` implements 
    - Functions to run calibration or projection simulations
    - The celery app instance

Jobs are orchestrated by

- `vic_celery_calibrate.py` which submits calibration tasks and produces the `calibration_results` folder
- `vic_celery_projection` which submits projection tasks and produces the `projection_results` folder

# Calibration tasks

Because the model output is stochastic, even the 'correct' parameter values may not result in an epidemic that fits the data due to stochastic effects. Calibration in this context consists of identifying beta-seed pairs that match the observed epidemic, with the idea that more samples will be selected with the best-fitting beta value, but we permit less likely samples with higher or lower beta values as well and include these in the projections. 

`vic_celery_calibrate.py` generates pairs of beta and seed values, 
 