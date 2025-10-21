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

inputFolder = './data'
outputFolder = './output'
data = pd.read_excel(f'{inputFolder}/data-extracted.xlsx')
column = 'Sus. dimensions'

columnFilename = {
    'Sus. dimensions' : 'sustainability_dim'
}
