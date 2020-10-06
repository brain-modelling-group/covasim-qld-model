#/usr/bin/bash
# Run calibration of QLD covid model up to END_DATE

# Paula Sanz-Leon, QIMR Berghofer September 2020
for x in {0..10}; do
    THIS_NUMBER=`bc <<< "scale=1; $x/1"`
    #echo $THIS_NUMBER
    python run_qld_wave_03.py --nruns 5 --case scenarios --par1 $THIS_NUMBER --end_simulation_date '2021-01-31'
done