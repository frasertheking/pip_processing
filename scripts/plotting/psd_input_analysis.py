import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_corr(df, size=12):
    df = df[['Log10_Nt', 'Log10_Sr', 'VVD', 'Log10_n0', 'Log10_eD', 'Log10_lambda', 'Log10_D0']]
    corr = df.corr()
    fig, ax = plt.subplots(figsize=(size, size))
    plt.title("PSD Variable Correlation Matrix")
    h = ax.matshow(corr, cmap='bwr', vmin=-1, vmax=1)
    # cbar = plt.colorbar(h)  # Assign colorbar to a variable
    fig.colorbar(h, ax=ax, label='Correlation')  # Use fig.colorbar() to make the colorbar the same height as the plot
    plt.xticks(range(len(corr.columns)), corr.columns)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.tight_layout()
    plt.savefig('corr.png')

df = pd.read_csv('final_data.csv')
df = df.dropna()
df = df[(df['eD'] >= 0) & (df['eD'] <= 4)]
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df['Log10_n0'] = df['n0'].apply(np.log)
df['Log10_lambda'] = df['lambda'].apply(np.log)
df['Log10_eD'] = df['eD'].apply(np.log)
df['Log10_D0'] = df['D0'].apply(np.log)
df['Log10_Sr'] = df['Sr'].apply(np.log)
df['Log10_Nt'] = df['Nt'].apply(np.log)
df.drop(columns=['n0', 'lambda', 'eD', 'D0', 'Sr', 'Nt'], inplace=True)
plot_corr(df)

# sns_plot = sns.pairplot(df, kind='kde', plot_kws={'levels': 2}, hue='NAME', height=3)
# sns_plot.map_upper(sns.kdeplot, levels=4, color=".2")
# sns_plot.savefig('output_kde.png')