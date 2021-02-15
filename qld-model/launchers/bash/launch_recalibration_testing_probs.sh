#/usr/bin/bash
# Run calibration of QLD covid model with different number of initial infections
# 

# Paula Sanz-Leon, QIMR Berghofer September 2020
for par2 in $(seq 0.45 0.05 0.55); do
    P2=$par2
    for par1 in $(seq 0.1 0.1 0.5); do
        P1=$par1
        python run_qld_model_refined_betas.py --ncpus 10 --nruns 5 --init_seed_infections 359 --global_beta 0.0105 \
                                      --par1 "$P1" --par2 "$P2" \
                                      --start_calibration_date '2020-03-01' --end_simulation_date '2020-04-25' --end_calibration_date '2020-03-30'\
                                      --layer_betas_file 'qld_model_layer_betas_01.csv' \
                                      --epi_calibration_file 'qld_epi_data_qld-health_calibration_2020-02-15_2020-03-30.csv'\
                                      --new_tests_mode 'mav'
    done
done
