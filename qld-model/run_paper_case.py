#!/usr/bin/env python
# coding: utf-8
"""
Replicate example from the paper - should create fig 8
=============================================================

"""


# Import IDM/Optima code
import covasim as cv


#  Define the simulation parameters 

pars = dict(pop_size = 200e3, 
	        pop_infected = 75, 
	        beta = 0.012,
            pop_type = 'hybrid', 
            start_day = '2020-02-10',
            end_day = '2020-06-29') 
trace_probs = dict(h= 0.9 , s= 0.7 , w= 0.7 , c= 0.3) 

trace_time = dict(h= 0 , s= 1 , w= 1 , c= 3 ) 

interventions = [ cv.clip_edges(days= ['2020-03-26'], changes=[0.0], layers=['s']), # 

cv.clip_edges(days= ['2020-03-26', '2020-04-10'],  changes= [0.7, 0.7], layers=['w', 'c']), 
#
cv.clip_edges(days= ['2020-04-10', '2020-05-05'], changes= [0.3, 0.3], layers=['w', 'c']), # 

cv.clip_edges(days= ['2020-05-05',  '2020-06-29'], changes=[0.8, 0.8], layers=['w', 'c']), # 

cv.test_prob(start_day= ['2020-05-20'] , symp_prob= 0.10 , symp_quar_prob= 0.8 , test_delay= 2 ), 

cv.contact_tracing(start_day= '2020-04-20', 
                   trace_probs=trace_probs, 
                   trace_time=trace_time) ]
 
sim  = cv.Sim(pars=pars, 
              interventions=interventions) 
sim.run() 
sim.plot() 