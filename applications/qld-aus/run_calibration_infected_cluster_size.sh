#/usr/bin/bash
# Run calibration of QLD covid model up to END_DATE

# Paula Sanz-Leon, QIMR Berghofer September 2020
for x in {0..10}; do
    THIS_NUMBER=$x
    #echo $THIS_NUMBER
    python run_qld_wave_02.py --nruns 5 --case calibration --cluster_size $THIS_NUMBER --end_calibration_date '2020-11-15'
done