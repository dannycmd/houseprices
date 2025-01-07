from pathlib import Path
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

### Load data
appDir = Path(os.path.abspath(''))
dataset = pd.read_csv(appDir / "pricepaidsample.csv", delimiter='\t', header=0, encoding="utf-8")
# remove missing postcodes and price paid values of zero
dataset = dataset[~((dataset['postcode'].isnull()) | (dataset['price_paid'] == 0))]
dataset['price_paid_mil'] = dataset['price_paid'] / 1000000

# density plot of price paid
fig, ax = plt.subplots()
sns.kdeplot(dataset['price_paid_mil'])
ax.set_xlabel('Price Paid (£m)')
ax.set_xlim(left=-5)
ax.set_ylim(bottom=-0.00005)
ax.set_title('Density Plot of Price Paid Sample (£m)')
ax.tick_params(bottom=True, left=True)
plt.show()

# summary stats
dataset.describe()

### postcode area to region lookup
outcodeRegion = pd.read_csv(appDir / "postcode_region_lookup.csv")
outcodeRegion['Area'] = outcodeRegion['Postcode prefix']
dataset['Area'] = dataset['Outcode'].replace('\d+', '', regex=True)
df = pd.merge(dataset, outcodeRegion, on="Area", how="left")

# filtering data for house prices <= £1m
df_filtered = df[df['price_paid_mil'] <= 1]

# ridge plot of log price paid by region
def ridgePlot(df, xVar, groups):
    sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
    palette = sns.color_palette("Set2", 12)
    g = sns.FacetGrid(df, palette=palette, row=groups, hue=groups, aspect=9, height=1.2)
    g.map_dataframe(sns.kdeplot, x=xVar, fill=True, alpha=1)
    g.map_dataframe(sns.kdeplot, x=xVar, color='black')

    def label(x, color, label):
        ax = plt.gca()
        ax.text(0, .2, label, color='black', fontsize=13,
                ha="left", va="center", transform=ax.transAxes)

    g.map(label, groups)
    g.figure.subplots_adjust(hspace=-.5)
    g.set_titles("")
    g.set(yticks=[], xlabel="Price Paid (£m)", ylabel="")
    g.despine(left=True)
    plt.suptitle("Price Paid Sample (<= £1m) by Region (£m)", y=0.98)

# ridgePlot(df, "log_price_paid_mil", "UK region")
ridgePlot(df_filtered, "price_paid_mil", "UK region")

#-> looks like all regions have the same type of distribution

### determining the distribution type
import scipy
import numpy as np

shape, location, scale = scipy.stats.lognorm.fit(df_filtered['price_paid_mil'])
mu, sigma = np.log(scale), shape
xmin, xmax = np.min(df_filtered['price_paid_mil']), np.max(df_filtered['price_paid_mil'])
x = np.linspace(xmin, xmax, 1000)

fig, ax = plt.subplots()
plt.plot(x, scipy.stats.lognorm.pdf(x, shape, location, scale), label="Lognormal")
sns.kdeplot(df_filtered, x="price_paid_mil", label="Density Plot")
ax.set_xlabel('Price Paid (£m)')
ax.set_ylim(bottom=-0.1)
ax.set_title('Price Paid Sample (£m) - Density Plot vs Fitted Lognormal Distribution')
ax.tick_params(bottom=True, left=True)
plt.legend(facecolor='white')
plt.show()

### QQ plot
import statsmodels.api as sm

df_filtered['log_price_paid_mil'] = np.log(df_filtered['price_paid_mil'])

fig, ax = plt.subplots(2, 1)
sm.qqplot(data=df_filtered['log_price_paid_mil'], line='s', ax=ax[0])
sns.kdeplot(df_filtered['log_price_paid_mil'], ax=ax[1])
ax[0].set_title('QQ Plot of Log Price Paid (£m, <= £1m) against Normal Distribution')
ax[0].tick_params(bottom=True, left=True)
ax[1].set_xlabel('Price Paid (£m)')
ax[1].set_ylim(bottom=-0.05)
ax[1].set_title('Density Plot of Log Price Paid (£m, <= £1m)')
ax[1].tick_params(bottom=True, left=True)
plt.tight_layout()
plt.show()