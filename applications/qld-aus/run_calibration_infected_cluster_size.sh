#/usr/bin/bash
# Run calibration of QLD covid model with different number of initial infections
# 

# Paula Sanz-Leon, QIMR Berghofer September 2020
for x in {1..10}; do
    THIS_NUMBER=$x
    #echo $THIS_NUMBER
    python run_qld_model.py --nruns 20 --init_seed_infections $THIS_NUMBER
done