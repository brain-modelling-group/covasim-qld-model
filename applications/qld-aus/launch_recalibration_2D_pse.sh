#/usr/bin/bash
# Run calibration of QLD covid model with different number of initial infections
# 

# Paula Sanz-Leon, QIMR Berghofer September 2020
for x in {1..50}; do
    THIS_NUMBER=$x
    for b in $(seq 0.01 0.0005 0.03); do
        BETA=$b
        #echo $THIS_NUMBER
        python run_qld_model_refined_betas.py --nruns 10 --init_seed_infections $THIS_NUMBER --global_beta $BETA --start_calibration_date '2020-02-15' --end_calibration_date '2020-05-15'
    done
done

# Do the same but for new tests that have been convolved
for x in {1..50}; do
    THIS_NUMBER=$x
    for b in $(seq 0.01 0.0005 0.03); do
        BETA=$b
        #echo $THIS_NUMBER
        python run_qld_model_refined_betas.py --nruns 10 --init_seed_infections $THIS_NUMBER --global_beta $BETA --start_calibration_date '2020-02-15' --end_calibration_date '2020-05-15' --new_tests_mode 'mav'
    done
done
