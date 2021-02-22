#/usr/bin/bash
PBS_ARRAY_INDEX=0
poisson_lambda=(0.1428 0.167 0.2 0.25 0.33 0.5 1.0 10.0 20.0 30.0 40.0 50.0)
P1="${poisson_lambda[$PBS_ARRAY_INDEX]}"
for iqf in $(seq 1.00 1.0 10.0); do
    IQF=$iqf
    python run_qld_model_resurgence.py --ncpus 4 --nruns 3 --label 'distributed' \
                                       --par1 "$P1" --iq_factor "$IQF"
done