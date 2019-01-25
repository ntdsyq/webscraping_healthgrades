import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
plt.style.use('ggplot')

r_fname = 'healthgrades_physicians_GI_NY_full_raw.csv'
fname = 'healthgrades_physicians_GI_NY_full.csv'
# Remove blank lines in raw csv file (scrapy bug for windows)
raw_data = pd.read_csv(r_fname)

# do not write index column
raw_data.to_csv(fname, index = False)  

# read in fixed csv file
data = pd.read_csv(fname) 

# check dimension, column names and types
data.shape
data.columns
for field in data.columns:
    print(field, type(data.loc[0,field]))

# age is float due to NaNs

# change zipcode to 5 digit string    
if data['zipcode'].dtype == 'int64':
    data['zipcode'] = data['zipcode'].apply(lambda x: '{0:05d}'.format(x))
data['zipcode']

# check some records    
pd.set_option('display.max_columns', 50)
data.head(5)
data.sample(10)
data.tail(5)    

# count missing values by column
mv_cols = pd.DataFrame(data = np.sum(data.isnull(), axis = 0) / data.shape[0], columns = ['pct_mv'] )
print(mv_cols.to_string(formatters = {'pct_mv': '{:.0%}'.format}))

# convert detailed doc_rating and staff_rating from string to float


