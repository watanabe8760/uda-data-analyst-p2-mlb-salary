# [Theme of analysis]
# Trend of salary
#   1. Time series of salary budget per team
#   2. Descriptive statistics per year
#   3. Time series of top players' salary
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

salaries = pd.read_csv('./lahman-csv_2015-01-24/Salaries.csv')
master = pd.read_csv('./lahman-csv_2015-01-24/Master.csv')
pitching = pd.read_csv('./lahman-csv_2015-01-24/Pitching.csv')
batting = pd.read_csv('./lahman-csv_2015-01-24/Batting.csv')


##### 1. Time series of salary budget per team
budget = salaries.groupby(['yearID', 'teamID'], as_index=False)['salary'].sum()
budget = budget.pivot(index='yearID', columns='teamID', values='salary')

for team in budget.columns:
    plt.plot(budget.index, budget[team], lw=2.0)
for team in budget.columns:
    # Only top and bottom teams are annotated
    if (budget.loc[2014, team] > 130e+06 or budget.loc[2014, team] < 70e+06):
        plt.annotate(team, xy=(2014, budget.loc[2014, team]))
#plt.legend(budget.columns, ncol=2, loc='upper left')
plt.title('Total Budget for Players\' Salary')
plt.xlabel('Year')
plt.ylabel('Budget')
plt.grid(True)
plt.show()

# Boxplot to see distribution (Only recent 3 years)
sns.boxplot(x='teamID', y='salary', \
            data=salaries[salaries['yearID'] == 2012], fliersize=0)
sns.boxplot(x='teamID', y='salary', \
            data=salaries[salaries['yearID'] == 2013], fliersize=0)
sns.boxplot(x='teamID', y='salary', \
            data=salaries[salaries['yearID'] == 2014], fliersize=0)



##### 2. Descriptive statistics per year
# Prepare DataFrame for summary satistics aggregation
yearstat = pd.DataFrame(index=salaries['yearID'].unique(), \
                        columns=['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'])
# Aggregate yearly summary statistics
for year, grouped in salaries.groupby('yearID', as_index=False)['salary']:
    yearstat.loc[year] = grouped['salary'].describe()

for stat in yearstat.columns.drop('count'):
    plt.plot(yearstat.index, yearstat[stat], lw=2.0)
plt.legend(yearstat.columns.drop('count'), loc='best')
plt.title('Summary Statistics of Salary')
plt.xlabel('Year')
plt.ylabel('Salary')
plt.grid(True)
plt.show()

# Plot without max to describe the other better
for stat in yearstat.columns.drop(['count', 'max']):
    plt.plot(yearstat.index, yearstat[stat], lw=2.0)
plt.legend(yearstat.columns.drop(['count', 'max']), loc='best')
plt.title('Summary Statistics of Salary without Max')
plt.xlabel('Year')
plt.ylabel('Salary')
plt.grid(True)
plt.show()

# Boxplot to see distribution
sns.boxplot(x='yearID', y='salary', data=salaries, fliersize=4, color='lightblue')
sns.stripplot(x='yearID', y='salary', data=salaries, jitter=1, size=4, linewidth=0.5)



##### 3. Time series of top players' salary
# Check who are pitchers and batters(fielders)
master['pitcher'] = master['playerID'].isin(pitching['playerID'].unique())
salaries = salaries.merge(master[['playerID', 'pitcher', 'nameGiven', 'nameLast']],\
                          how='left', on='playerID')
salaries['fullname'] = salaries['nameGiven'].str.cat(salaries['nameLast'], sep=' ')

# Aggregate top 10 pitchers and batters
topPitSal = pd.DataFrame(columns=['yearID', 'rank', 'fullname', 'salary'])
topBatSal = pd.DataFrame(columns=['yearID', 'rank', 'fullname', 'salary'])
for gid, grouped in salaries.groupby(['yearID', 'pitcher'], as_index=False):
    grouped.sort_values(by='salary',ascending=False, inplace=True)
    grouped['rank'] = np.linspace(1, grouped.shape[0], grouped.shape[0])
    if gid[1]:
        topPitSal = \
            topPitSal.append(grouped[['yearID', 'rank', 'fullname', 'salary']].iloc[0:10])
    else:
        topBatSal = \
            topBatSal.append(grouped[['yearID', 'rank', 'fullname', 'salary']].iloc[0:10])

topPitSal4G = topPitSal.pivot(index='yearID', columns='rank', values='salary')
topBatSal4G = topBatSal.pivot(index='yearID', columns='rank', values='salary')
rankLegend = ['Top','2nd','3rd','4th','5th','6th','7th','8th','9th','10th']


for rank in topPitSal4G.columns:
    plt.plot(topPitSal4G.index, topPitSal4G[rank].astype(int), lw=2.0)
plt.legend(rankLegend, loc='best', title='Rank')
plt.title('Top 10 Pitchers\' Salary')
plt.xlabel('Year')
plt.ylabel('Salary')
plt.show()

for rank in topBatSal4G.columns:
    plt.plot(topBatSal4G.index, topBatSal4G[rank].astype(int), lw=2.0)
plt.legend(rankLegend, loc='best', title='Rank')
plt.title('Top 10 Batters\' Salary')
plt.xlabel('Year')
plt.ylabel('Salary')
plt.grid(True)
plt.show()

