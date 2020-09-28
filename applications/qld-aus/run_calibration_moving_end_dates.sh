#/usr/bin/bash
# Run calibration of QLD covid model up to END_DATE

# Paula Sanz-Leon, QIMR Berghofer September 2020


START_DATE="$(date -d "2020-07-05" +%s)"
END_DATE="$(date -d "2020-08-04" +%s)"

while [[ "$START_DATE" -le "$END_DATE" ]]; do 
    THIS_DATE="$(date -d "@$START_DATE" +%F)"
    echo $THIS_DATE
    python run_qld_wave_02.py --nruns 20 --case calibration --end_calibration_date "$THIS_DATE" 
    let START_DATE+=86400;
done