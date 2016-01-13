# [Theme of analysis]
# Does wOBA reflect the level of salary?
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

master = pd.read_csv('./lahman-csv_2015-01-24/Master.csv')
batting = pd.read_csv('./lahman-csv_2015-01-24/Batting.csv')
pitching = pd.read_csv('./lahman-csv_2015-01-24/Pitching.csv')
salaries = pd.read_csv('./lahman-csv_2015-01-24/Salaries.csv')
factor = pd.read_csv('./fangraphs/FanGraphs Leaderboard.csv')

# Data cleasing - batting
batting.fillna(0, inplace=True)
batting['uBB'] = batting.BB - batting.IBB

# Remove pitchers
batting = batting[batting.playerID.isin(pitching.playerID.unique())]
# Remove players whose AB (At Bat) is 0 or blank
batting = batting[batting.AB > 0]
# Remove players before 1985 when Salary data is not available
batting = batting[batting.yearID >= 1985]

# Add salary data to batting
batting = batting.merge(salaries[['yearID', 'playerID', 'salary']], \
                        how='left', on=['yearID', 'playerID'])
# Remove rows where salary data is not available
batting = batting[pd.notnull(batting.salary)]


# Birth countries
master.groupby('birthCountry')['birthCountry'].count()
# Weight and height
master.plot.scatter(x='weight', y='height')
body = master.groupby(['weight', 'height'], as_index=False)['playerID'].count()
plt.scatter(x=body['weight'], y=body['height'], s=body['playerID']/5)
# Salaries
salaries['salary'].describe()
salaries['salary'].plot.hist(bins=200)
salaries.loc[salaries.yearID == 2014]['salary'].plot.hist(bins=200)
salaries.loc[salaries.yearID == 2013]['salary'].plot.hist(bins=200)
salaries.loc[salaries.yearID == 2012]['salary'].plot.hist(bins=200)

plt.hist(salaries.salary, bins=100, normed=True, log=True)

# Batting
batting.describe()
batting.G.plot.hist(bins=50)
batting.AB.plot.hist(bins=50)

def getwOBA(f, b):
    # Return Weighted On-Base Average (wOBA)
    # 
    # Args:
    #   f: DataFrame, factors of wOBA ("FanGraphs Leaderboard.csv")
    #   b: DataFrame, batting performance ("Batting.csv")
    # 
    # Return:
    #   wOBA
    # 
    # Foluma:
    #   (f1*uBB + f2*HBP + f3*H + f4*2B + f5*3B + f6*HR) /
    #                                           (AB + BB - IBB + SF + HBP)
    # Terms:
    #   fn : weight factor (yearly)
    #   uBB: Unintentional BB
    #   HBP: Hit By Pitch
    #   H  : Hits
    #   2B : Doubles
    #   3B : Triples
    #   HR : Homeruns
    #   AB : At Bat
    #   BB : Bases on Balls
    #   IBB: Intentional BB
    #   SF : Sacrifice Flies
    # 
    return (f.wBB.values*b.uBB + f.wHBP.values*b.HBP + f.w1B.values*b.H + \
            f.w2B.values*b['2B'] + f.w3B.values*b['3B'] + f.wHR.values*b.HR) / \
           (b.AB + b.BB - b.IBB + b.SF + b.HBP)

# Compute wOBA for all players
wOBA = pd.DataFrame()
for y in batting.yearID.unique():
    b = batting[batting.yearID == y]
    f = factor[factor.Season == y]
    df = pd.DataFrame({
        "playerID": b.playerID.values,
        "yearID": b.yearID.values,
        "stint": b.stint.values,
        "wOBA" : getwOBA(f, b)
    })
    wOBA = wOBA.append(df)

# Add wOBA to batting DataFrame
batting = batting.merge(wOBA, how='left', on=['playerID', 'yearID', 'stint'])
# wOBA exploratory analysis
batting.wOBA.plot.hist(bins=100)
batting.wOBA.sort_values(ascending=False, na_position='last')
batting.wOBA[batting.AB >= 50].sort_values(ascending=False, na_position='last')
batting.wOBA[batting.AB >= 50].hist(bins=100)
batting.wOBA[batting.G >= 25].hist(bins=100)

# Salary exploratory analysis
batting.salary.hist(bins=100)
plt.hist(np.log(batting.salary.values), bins=100)

np.corrcoef(batting['2B'], batting.H)