#/usr/bin/bash
# Run calibration of QLD covid model with different number of initial infections
# 

# Paula Sanz-Leon, QIMR Berghofer September 2020
for x in {1..25}; do
    THIS_NUMBER=$x
    for b in $(seq 0.01 0.0005 0.03); do
    	BETA=$b
        #echo $THIS_NUMBER
        python run_qld_model.py --nruns 5 --init_seed_infections $THIS_NUMBER --global_beta $BETA --end_calibration_date '2020-03-30'
    done
done