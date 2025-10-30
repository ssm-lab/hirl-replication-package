from upsetplot import from_memberships
from upsetplot import plot
from matplotlib import pyplot
import matplotlib
from itertools import combinations

import numpy as np
import os
import pandas as pd
from collections import Counter
from matplotlib import pyplot as plt
from matplotlib.offsetbox import AnchoredText
from matplotlib.ticker import MaxNLocator
import plot_likert

inputFolder = './data'
outputFolder = './output'

data = pd.read_excel(f'{inputFolder}/P1-1-30.xlsx')
data_df.index = pd.to_datetime(data_df.index) #convert index column into DateTime column data_df.plot()
into DateTime column data_df.plot()

data = pd.DataFrame({'Q1': {0: 'Strongly disagree', 1: 'Agree', ...},
                     'Q2': {0: 'Disagree', 1: 'Strongly agree', ...}})

plot_likert.plot_likert(data, plot_likert.scales.agree, plot_percentage=True);
