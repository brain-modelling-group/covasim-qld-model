import covasim as cv
import pandas as pd
import sciris as sc



T = sc.tic()

# Import files
msim60 = sc.loadobj('covasim60.msim')
msim70 = sc.loadobj('covasim70.msim')


p50_60 = len([i for i in range(100) if msim60.sims[i].results['new_diagnoses'].values[-1]>50])
p100_60 = len([i for i in range(100) if msim60.sims[i].results['new_diagnoses'].values[-1]>100])

p50_70 = len([i for i in range(100) if msim70.sims[i].results['new_diagnoses'].values[-1]>50])
p100_70 = len([i for i in range(100) if msim70.sims[i].results['new_diagnoses'].values[-1]>100])

output  = f' Probability of an outbreak exceeding 50 under July 31 settings: {p50_70} \n'
output += f'Probability of an outbreak exceeding 100 under July 31 settings: {p100_70} \n'
output += f'      Probability of an outbreak exceeding 50 with reduced risk: {p50_60} \n'
output += f'     Probability of an outbreak exceeding 100 with reduced risk: {p100_60} \n'
print(output)
sc.toc(T)