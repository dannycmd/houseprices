from pathlib import Path
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import QuantileTransformer
import numpy as np
import statsmodels.api as sm

### Load data
appDir = Path(os.path.abspath('')).parent
summary = pd.read_csv(appDir / 'app/summary.csv', encoding='utf-8', delimiter=',')
summary = summary[(~summary['Outcode'].isnull())]
summary = summary.rename(columns={"range_": "range"})

fig, ax = plt.subplots(2, 1, figsize=(10,12))

summary['median_mil'] = summary['median'] / 1000000
summary['log_median_mil'] = np.log(summary['median_mil'])

fig, ax = plt.subplots(2, 1, figsize=(10, 12))
sns.kdeplot(data=summary, x='median_mil', ax=ax[0])
sm.qqplot(summary['median_mil'], ax=ax[1])
ax[0].set_xlabel('Price Paid Medians (£m)')
ax[0].set_xlim(left=-5)
ax[0].set_ylim(bottom=-0.005)
ax[0].set_title('Density Plot of Price Paid Sample Medians (£m)')
ax[0].tick_params(bottom=True, left=True)
ax[1].set_title('QQ Plot of Price Paid Sample Medians (£m)')
plt.show()

qt = QuantileTransformer(output_distribution='normal', random_state=0)
values = qt.fit_transform(np.array(list(summary['median_mil'])).reshape(-1, 1)).flatten()

fig, ax = plt.subplots(2, 1, figsize=(10, 12))
sm.qqplot(data=np.array(values), ax=ax[1])
sns.kdeplot(data=values, ax=ax[0])
ax[0].set_xlabel('Quantile Transformed Price Paid Medians (£m)')
ax[0].set_xlim(left=-5)
ax[0].set_ylim(bottom=-0.005)
ax[0].set_title('Density Plot of Quantile Transformed Price Paid Sample Medians (£m)')
ax[0].tick_params(bottom=True, left=True)
ax[1].set_title('QQ Plot of Quantile Transformed Price Paid Sample Medians (£m)')

plt.tight_layout()
plt.show()

sm.qqplot(data=summary['median_mil'], ax=ax[1])
sns.kdeplot(data=summary['median_mil'], ax=ax[0])
ax[0].set_xlabel('Price Paid (£m)')
ax[0].set_xlim(left=0.0)
ax[1].set_ylim(bottom=0.0)
ax[0].set_title('Density Plot of Price Paid Sample with Quantile Transformation (£m)')
ax[1].set_title('QQ Plot of Price Paid Sample with Quantile Transformation (£m)')

plt.tight_layout()
plt.show()