# [Theme of analysis]
# Relationship between salary and performance
#   1. Correlation between salary and performance measurements
#   2. Linear Regression to estimate salary
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as smf
from scipy.stats.stats import pearsonr

salaries = pd.read_csv('./lahman-csv_2015-01-24/Salaries.csv')
pitching = pd.read_csv('./lahman-csv_2015-01-24/Pitching.csv')
batting = pd.read_csv('./lahman-csv_2015-01-24/Batting.csv')

# Change column names which start with number
batting.rename(columns={"2B":"H2B", "3B":"H3B"}, inplace=True)
# Add total batting performance measurement
batting['TH'] = batting['H'] + batting['H2B'] + batting['H3B'] + batting['HR']

# Set concatenation of key column values as index
pitching.index = pitching['yearID'].astype(str) + pitching['teamID'].astype(str) + \
                 pitching['playerID'].astype(str)
batting.index = batting['yearID'].astype(str) + batting['teamID'].astype(str) + \
                batting['playerID'].astype(str)                 
# Drop pitchers' batting performance
batting = batting[~batting.index.isin(pitching.index)]



##### 1. Correlation between salary and performance measurements
# Merge salaries and performance data
#  [Assumption]
#    Salary is determined by the previous year's result
#     Performance    Salary
#        2013  ---->  2014
#        2012  ---->  2013
#        2011  ---->  2012
#        ....         ....
salaries['yearBasedOn'] = salaries['yearID'] - 1
pitching = pitching.merge(salaries, how='left', \
                          left_on=['yearID', 'teamID', 'lgID', 'playerID'], \
                          right_on=['yearBasedOn', 'teamID', 'lgID', 'playerID'])
batting = batting.merge(salaries, how='left', \
                        left_on=['yearID', 'teamID', 'lgID', 'playerID'], \
                        right_on=['yearBasedOn', 'teamID', 'lgID', 'playerID'])
# Rename and distinguish yearID: 
#  - Performance year ID: pyearID
#  - Salary yera ID:      syearID
pitching.rename(columns={"yearID_x":"pyearID", "yearID_y":"syearID"}, inplace=True)
batting.rename(columns={"yearID_x":"pyearID", "yearID_y":"syearID"}, inplace=True)
# Remove unnecessary column used for merge
pitching.drop('yearBasedOn', axis=1, inplace=True)
batting.drop('yearBasedOn', axis=1, inplace=True)
# Drop rows whose salary data is not available
pitching = pitching[pitching['salary'].notnull()]
batting = batting[batting['salary'].notnull()]


# Compute rate of measurement
# To simplify the process, the following rule is applied.
#  Pitching performance:
#   - All measurements are devided by G (Number of Game)
#  Batting performance:
#   - All measurements are devided by AB (At Bat)
NON_PERFORMANCE_COLUMNS = ['playerID', 'pyearID', 'stint', 'teamID', \
                           'lgID', 'syearID', 'salary']
for col in pitching.columns.drop(NON_PERFORMANCE_COLUMNS):
    if col == 'G': 
        continue
    else:
        pitching[col + 'r'] = pitching[col] / pitching['G']
        pitching.loc[pitching['G'] == 0, col + 'r'] = 0
        

for col in batting.columns.drop(NON_PERFORMANCE_COLUMNS):
    if col == 'AB':
        continue
    else:
        batting[col + 'r'] = batting[col] / batting['AB']
        batting.loc[batting['AB'] == 0, col + 'r'] = 0


# Correlation matrix for 2014
pit_recent = pitching[pitching['syearID'] == 2014]
bat_recent = batting[batting['syearID'] == 2014]
# 
pit_recent.shape
bat_recent.shape

# None check
pit_recent.apply(lambda col: sum(col.isnull()))
bat_recent.apply(lambda col: sum(col.isnull()))

# Number of game related
sns.pairplot(pit_recent, vars=['W', 'L', 'G', 'GS', 'GF', 'CG', 'salary'])
# Positive measures
sns.pairplot(pit_recent, vars=['SHO', 'SV', 'IPouts', 'SO', 'salary'])
# Negative measures
sns.pairplot(pit_recent, vars=['H', 'ER', 'HR', 'BB', 'ERA', 'R', 'salary'])
sns.pairplot(pit_recent, vars=['IBB', 'WP', 'HBP', 'BK', 'SH', 'SF', 'salary'])

# Correlation matrix on the original measurement (batters)
# Number of game related
sns.pairplot(bat_recent, vars=['G', 'AB', 'salary'])
# Positive measures
sns.pairplot(bat_recent, vars=['H', 'H2B', 'H3B', 'HR', 'TH', 'salary'])
sns.pairplot(bat_recent, vars=['R', 'RBI', 'SB', 'BB', 'IBB', 'salary'])
# Negative measures
sns.pairplot(bat_recent, vars=['CS', 'SO', 'GIDP', 'salary'])
sns.pairplot(bat_recent, vars=['HBP', 'SH', 'SF', 'salary'])


# Correlation matrix on the rate measurement (pitchers)
# Number of game related
sns.pairplot(pit_recent, vars=['Wr', 'Lr', 'G', 'GSr', 'GFr', 'CGr', 'salary'])
# Positive measures
sns.pairplot(pit_recent, vars=['SHOr', 'SVr', 'IPoutsr', 'SOr', 'salary'])
# Negative measures
sns.pairplot(pit_recent, vars=['Hr', 'ERr', 'HRr', 'BBr', 'ERAr', 'Rr', 'salary'])
sns.pairplot(pit_recent, vars=['IBBr', 'WPr', 'HBPr', 'BKr', 'SHr', 'SFr', 'salary'])

# Correlation matrix on the rate measurement (batters)
# Number of game related
sns.pairplot(bat_recent, vars=['Hr', 'H2Br', 'H3Br', 'HRr', 'THr', 'salary'])
sns.pairplot(bat_recent, vars=['Rr', 'RBIr', 'SBr', 'BBr', 'IBBr', 'salary'])
# Negative measures
sns.pairplot(bat_recent, vars=['CSr', 'SOr', 'GIDPr', 'salary'])
sns.pairplot(bat_recent, vars=['HBPr', 'SHr', 'SFr', 'salary'])


# Pearson correlation and P value
print pearsonr(pit_recent['W'], pit_recent['salary'])
print pearsonr(pit_recent['L'], pit_recent['salary'])
print pearsonr(pit_recent['G'], pit_recent['salary'])
print pearsonr(pit_recent['GS'], pit_recent['salary'])
print pearsonr(pit_recent['GF'], pit_recent['salary'])

print pearsonr(bat_recent['H'], bat_recent['salary'])
print pearsonr(bat_recent['H2B'], bat_recent['salary'])
print pearsonr(bat_recent['H3B'], bat_recent['salary'])
print pearsonr(bat_recent['HR'], bat_recent['salary'])
print pearsonr(bat_recent['TH'], bat_recent['salary'])



##### 2. Linear Regression to estimate salary
# Check null value
for col in pitching.columns:
    print col, sum(pitching[col].isnull())
for col in batting.columns:
    print col, sum(batting[col].isnull())

def get_formula(df):
    # Create a formula to estimate salary
    # 
    # Args:
    #   df: DataFrame, pitching or batting
    # Return:
    #   A formula string
    #
    formula = ""
    for col in df.columns.drop(NON_PERFORMANCE_COLUMNS):
        if sum(df[col].isnull()) > 0:
            if sum(df[col].notnull()) > df.shape[0] / 2:
                # If more than a half is null, the column is not added
                # Fill null by mean if less than a half is null
                df.loc[df[col].isnull(), col] = df[col].mean()
                if formula == "":
                    formula = col
                else:
                    formula = formula + " + " + col
        else:
            if formula == "":
                formula = col
            else:
                formula = formula + " + " + col
    return "salary ~ " + formula
    

# Fit linear regression
with open("olm_summary_pitcher.txt", "w") as f:
    for y in pitching['syearID'].unique():
        target = pitching[pitching['syearID'] == y]
        model = smf.ols(formula=get_formula(target), data=target).fit()
        tval = model.tvalues
        print "Year: " + str(y)
        print tval[(tval > 2) + (tval < -2)]
        print "\n"
        f.write("Year : " + str(y) + "\n")
        f.write(model.summary().as_text())
        f.write("\n\n\n")

with open("olm_summary_batter.txt", "w") as f:
    for y in batting['syearID'].unique():
        target = batting[batting['syearID'] == y]
        model = smf.ols(formula=get_formula(target), data=target).fit()
        tval = model.tvalues
        print "Year: " + str(y)
        print tval[(tval > 2) + (tval < -2)]
        print "\n"
        f.write("Year : " + str(y) + "\n")
        f.write(model.summary().as_text())
        f.write("\n\n\n")

