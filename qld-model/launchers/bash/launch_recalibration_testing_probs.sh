#/usr/bin/bash
# Run calibration of QLD covid model with different number of initial infections
# 
# Paula Sanz-Leon, QIMR Berghofer Feb 2021
# for par2 in $(seq 0.0 0.05 0.05); do
#     P2=$par2
#     for par1 in $(seq 0.0 0.05 0.05); do
#         P1=$par1
        python run_qld_model_refined_betas.py --ncpus 10 --nruns 5 --init_seed_infections 62 --global_beta 0.014 \
                                      --par1 0.0 --par2 0.0 \
                                      --start_calibration_date '2020-02-15' --end_simulation_date '2020-04-25' --end_calibration_date '2020-03-30'\
                                      --layer_betas_file 'qld_model_layer_betas_02.csv' \
                                      --epi_calibration_file 'qld_epi_data_qld-health_calibration_2020-02-15_2020-03-30.csv'\
                                      --new_tests_mode 'raw'



        # python run_qld_model_refined_betas.py --ncpus 10 --nruns 5 --init_seed_infections 99 --global_beta 0.0105 \
        #                               --par1 0.0 --par2 0.0 \
        #                               --start_calibration_date '2020-02-15' --end_simulation_date '2020-05-15' --end_calibration_date '2020-05-15'\
        #                               --layer_betas_file 'qld_model_layer_betas_01.csv' \
        #                               --epi_calibration_file 'qld_epi_data_qld-health_calibration_2020-02-15_2020-05-15.csv'\
        #                               --new_tests_mode 'raw'

#     done
# done
