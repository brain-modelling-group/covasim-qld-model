#/usr/bin/bash
# Run calibration of QLD covid model with different number of initial infections
# 

# Paula Sanz-Leon, QIMR Berghofer September 2020
for par1 in $(seq 1.0 0.002 1.1);; do
    P1=$par1
    for par2 in $(seq 1.0 0.025 1.5); do
        P2=$par2
        python run_qld_model_refined_betas.py --ncpus 10 --nruns 10 --init_seed_infections 99 --global_beta 0.0105 \
                                      --p1 "$P1" --p2 "$P2" \
                                      --start_calibration_date '2020-02-15' --end_simulation_date '2020-04-10' --end_calibration_date '2020-03-30'\
                                      --layer_betas_file 'qld_model_layer_betas_01.csv' \
                                      --epi_calibration_file 'qld_epi_data_qld-health_calibration_2020-02-15_2020-03-30.csv'\
                                      --new_tests_mode 'mav'
    done
done
