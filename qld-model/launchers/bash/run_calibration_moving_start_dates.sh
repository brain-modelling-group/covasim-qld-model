#/usr/bin/bash
# Run calibration of QLD covid model with different stating dates. 
# Paula Sanz-Leon, QIMR Berghofer February 2021


START_DATE="$(date -d "2020-01-01" +%s)"
END_DATE="$(date -d "2020-02-15" +%s)"

while [[ "$START_DATE" -le "$END_DATE" ]]; do 
    THIS_DATE="$(date -d "@$START_DATE" +%F)"
    echo $THIS_DATE
    for x in {1..15}; do
        THIS_NUMBER=$x
	    python run_qld_model_refined_betas.py --nruns 10 --init_seed_infections "$THIS_NUMBER" --global_beta 0.014 \
	                                          --start_calibration_date "$THIS_DATE" --end_calibration_date '2020-03-30'\
	                                          --end_simulation_date '2020-04-10' \
	                                          --layer_betas_file 'qld_model_layer_betas_01.csv' \
	                                          --epi_calibration_file 'qld_epi_data_qld-health_calibration_2020-02-15_2020-03-30.csv'\
	                                          --new_tests_mode 'mav'
    done
    let START_DATE+=86400;
done
