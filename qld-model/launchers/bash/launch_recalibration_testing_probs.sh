#/usr/bin/bash
# Run calibration of QLD covid model with different number of initial infections
# 
# Paula Sanz-Leon, QIMR Berghofer Feb 2021
for par1 in $(seq 0.05 0.05 0.1); do
    P1=$par1
        python run_qld_model_optimise_testing.py --ncpus 10 --nruns 5 --init_seed_infections 150 --global_beta 0.014 \
                                      --p1 "$P1" \
                                      --start_calibration_date '2020-03-01' --end_simulation_date '2020-04-05' --end_calibration_date '2020-04-05'\
                                      --layer_betas_file 'qld_model_layer_betas_01.csv' \
                                      --epi_calibration_file 'qld_epi_data_qld-health_calibration_2020-02-15_2020-05-15_mav05.csv'\
                                      --new_tests_mode 'mav05'
done