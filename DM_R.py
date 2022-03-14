import pandas as pd
import matplotlib.pyplot as plt

# Read the data from excel file
data = pd.read_excel('Online Retail.xlsx')

# To print number of rows, column, entries, etc.
print(data.info())

# Customer ID cannot be null
data= data[pd.notnull(data['CustomerID'])]

# Convert to show date only
from datetime import datetime
data["InvoiceDate"] = data["InvoiceDate"].dt.date
# Create date variable that helps records recency
import datetime
today = max(data.InvoiceDate) + datetime.timedelta(days=1)

# Total price of each line.
data["TotalPrice"] = data["Quantity"] * data["UnitPrice"]

# Groupby how many times did a customer purchase. 
table = data.groupby(['CustomerID']).agg({
    'InvoiceDate': lambda x: (today - x.max()).days, # Recency
    'InvoiceNo': 'count', # Frequency
    'TotalPrice': 'sum'}) # Monetary

# One row per customer with their RFM scores stored in columns.
table.rename(columns = {'InvoiceDate': 'Recency',
                            'InvoiceNo': 'Frequency',
                            'TotalPrice': 'Monetary'}, inplace=True)

# The entire population is divided into five equal quintiles for each parameter.
quintiles = table[['Recency', 'Frequency', 'Monetary']].quantile([.1667, .3334, .5, .6667, .8334]).to_dict()

# Methods to assign scores from 1 to 5. 
# A smaller Recency value is assigned a higher score.
def r_score(x): 
    if x <= quintiles['Recency'][.1667]:
        return 5
    elif x <= quintiles['Recency'][.3334]:
        return 4
    elif x <= quintiles['Recency'][.5]:
        return 3
    elif x <= quintiles['Recency'][.6667]:
        return 2
    elif x <= quintiles['Recency'][.8334]:
        return 1
    else:
        return 0

# Higher Frequency and Monetary values are assigned a higher score.
def fm_score(x, c):
    if x <= quintiles[c][.1667]:
        return 0
    elif x <= quintiles[c][.3334]:
        return 1
    elif x <= quintiles[c][.5]:
        return 2
    elif x <= quintiles[c][.6667]:
        return 3
    elif x <= quintiles[c][.8334]:
        return 4
    else:
        return 5    

# R, F and M scores of each customer.
table['R'] = table['Recency'].apply(lambda x: r_score(x))
table['F'] = table['Frequency'].apply(lambda x: fm_score(x, 'Frequency'))
table['M'] = table['Monetary'].apply(lambda x: fm_score(x, 'Monetary'))

# Average of Frequency and Monetary value to be plotted against Recency
table['Combined FM'] = (table['F'] + table['M'])/2
table['Combined FM'] = table['Combined FM'].astype(int)

custmor_segments = {
    r'[4-5][4-5]': 'Champions',
    r'[2-5][3-5]': 'loyal customers',
    r'[3-5][1-3]': 'Potential loyalists',
    r'[4-5][0-1]': 'Recent customers',
    r'[3-4][0-1]': 'Promising',
    r'[2-3][2-3]': 'Need attention',
    r'[2-3][0-2]': 'About to sleep',
    r'[0-2][2-5]': 'At risk',
    r'[0-1][4-5]': 'Can\'t loose',
    r'[1-2][1-2]': 'Hibernating',
    r'[0-2][0-2]': 'Lost',
}

table['Segment'] = table['R'].map(str) + table['Combined FM'].map(str)
table['Segment'] = table['Segment'].replace(custmor_segments, regex=True)
print(table.head())

# To count the number of customers in each segment
segments_counts = table['Segment'].value_counts().sort_values(ascending=True)

fig, ax = plt.subplots()

bars = ax.barh(range(len(segments_counts)),
              segments_counts,
              color='silver')
ax.set_frame_on(False)
ax.tick_params(left=False,
               bottom=False,
               labelbottom=False)
ax.set_yticks(range(len(segments_counts)))
ax.set_yticklabels(segments_counts.index)

for i, bar in enumerate(bars):
        value = bar.get_width()
        ax.text(value,
                bar.get_y() + bar.get_height()/2,
                '{:,} ({:}%)'.format(int(value),
                                   int(value*100/segments_counts.sum())),
                va='center',
                ha='left'
               )

plt.show()