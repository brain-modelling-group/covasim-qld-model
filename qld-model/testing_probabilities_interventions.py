# Testing probabilties of symptomatic -- from NSW cases
    symp_test_prob_prelockdown = 0.000  # Limited testing pre lockdown
    symp_test_prob_lockdown = 0.0#0.012      # 0.065 #Increased testing during lockdown
    
    initresponse_date = '2020-03-05'
    initresponse2_date = '2020-03-10'
    initresponse3_date = '2020-03-15'
    initresponse4_date = '2020-03-20'
    lockdown_date = '2020-03-30' # Lockdown date in QLD
    reopen_date   = '2020-05-15' # Reopen shops etc date in QLD-NSW
    reopen2_date  = '2020-12-01' # Start of stage 6 in QLD

    sim.pars['interventions'].append(cv.test_prob(start_day=input_args.start_calibration_date, 
                                                  end_day=initresponse_date, 
                                                  symp_prob=symp_test_prob_prelockdown, 
                                                  asymp_quar_prob=0.0, do_plot=False))

    sim.pars['interventions'].append(cv.test_prob(start_day=initresponse_date, 
                                                  end_day=initresponse2_date, 
                                                  symp_prob=0.000, 
                                                  asymp_quar_prob=0.00, do_plot=False))

    sim.pars['interventions'].append(cv.test_prob(start_day=initresponse2_date, 
                                                   end_day=initresponse3_date, 
                                                   symp_prob=0.0,#0.016, 
                                                   asymp_quar_prob=0.00, do_plot=False))

    sim.pars['interventions'].append(cv.test_prob(start_day=initresponse3_date, 
                                                   end_day=initresponse4_date, 
                                                   symp_prob=0.0,#0.014, 
                                                   asymp_quar_prob=0.00, do_plot=False))

    sim.pars['interventions'].append(cv.test_prob(start_day=initresponse4_date, 
                                                   end_day=lockdown_date, 
                                                   symp_prob=0.0,#0.01, 
                                                   asymp_quar_prob=0.01, do_plot=False))

    sim.pars['interventions'].append(cv.test_prob(start_day=lockdown_date, 
                                                    end_day=reopen_date, 
                                                    symp_prob=symp_test_prob_lockdown, 
                                                    asymp_quar_prob=0.01,do_plot=False))

    if sim.day(input_args.end_simulation_date) > sim.day(reopen_date):     
        # More assumptions from NSW
        symp_test_prob_postlockdown = 0.19 # 0.165 # Testing since lockdown
        asymp_quar_prob_postlockdown = (1.0-(1.0-symp_test_prob_postlockdown)**10)
        
        sim.pars['interventions'].append(cv.test_prob(start_day=reopen_date, 
                                                      end_day=reopen2_date, 
                                                      symp_prob=symp_test_prob_postlockdown, 
                                                      asymp_quar_prob=asymp_quar_prob_postlockdown,do_plot=True))

    if sim.day(input_args.end_simulation_date) > sim.day(reopen2_date):
        # Future interventions, from start of stage 6 onwards
        symp_test_prob_future = 0.9 # From NSW cases
        asymp_quar_prob_future = (1.0-(1.0-symp_test_prob_future)**10)/2.0 

        sim.pars['interventions'].append(cv.test_prob(start_day=reopen2_date, 
                                                      symp_prob=symp_test_prob_future, 
                                                      asymp_quar_prob=asymp_quar_prob_future,do_plot=True))



      ################################# BAD BAD BAD TESTING #######################################
    # HOW NOT TO FIT RESULTS
    sim.pars['interventions'].append(cv.test_num(daily_tests=new_tests[sim.day(input_args.start_calibration_date):sim.day('2020-03-15')], 
                                                 start_day=input_args.start_calibration_date, 
                                                 end_day  ='2020-03-14',
                                                 symp_test = 60.0))


    sim.pars['interventions'].append(cv.test_num(daily_tests=new_tests[sim.day('2020-03-15'):sim.day('2020-03-21')], 
                                                                      start_day='2020-03-15', 
                                                                      end_day  ='2020-03-20',
                                                                      symp_test = 95.0))

    sim.pars['interventions'].append(cv.test_num(daily_tests=new_tests[sim.day('2020-03-21'):sim.day('2020-03-31')], 
                                                                      start_day='2020-03-21', 
                                                                      end_day  ='2020-03-31',
                                                                      symp_test = 100.0))

    sim.pars['interventions'].append(cv.test_prob(start_day='2020-03-15', 
                                                  end_day='2020-03-30', 
                                                  symp_prob=0.0, 
                                                  asymp_prob=0.03, do_plot=False))

    sim.pars['interventions'].append(cv.test_prob(start_day='2020-03-31', 
                                                  end_day='2020-04-15', 
                                                  symp_prob=0.0, 
                                                  asymp_prob=0.025, do_plot=False))

    sim.pars['interventions'].append(cv.test_prob(start_day='2020-04-15', 
                                                  end_day='2020-05-15', 
                                                  symp_prob=0.0, 
                                                  asymp_prob=0.015, do_plot=False))