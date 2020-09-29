#/usr/bin/bash
# Run calibration of QLD covid model up to END_DATE

# Paula Sanz-Leon, QIMR Berghofer September 2020
for x in {1..10}; do
    THIS_NUMBER=`bc <<< "scale=1; $x/20"`
    #echo $THIS_NUMBER
    python run_qld_wave_02.py --nruns 10 --case scenarios --par1 $THIS_NUMBER --end_simulation_date '2020-11-30'
done