### Usage: python recommender_predict.py datafile modeldir <pearson|cosine>
### Example: python recommender_predict.py effectiveness_test.csv models
### Example: python recommender_predict.py effectiveness_test.csv models pearson

### Takes in a single user's effectiveness measurements and determines what the most and least effect treatements for them will be

import numpy as np
import pandas as pd
import sys
import functools

if len(sys.argv) < 3:
    print "Usage: python recommender_predict.py datafile modelfile distance_metric"
    quit()

file = sys.argv[1]
modeldir = sys.argv[2]

test_df = pd.read_csv(file)

distance_metric = 'cosine'
if len(sys.argv) == 4:
    if (sys.argv[3] == 'pearson') or (sys.argv[3] == 'cosine'):
        distance_metric = sys.argv[3]
    else:
        print "distance metric must be pearson or cosine"
        quit()

def find_closest(x, treatment_correlations):
    highestCorrelationValue = 0
    highestCorrelationKey = ""
    for treatment1 in x:
        if treatment1 in treatment_correlations.index:
            treatment2_column = treatment_correlations.index[treatment1].idxmax(axis=1)
            print treatment2_column
            if treatment_correlations[treatment2_column] > highestCorrelationValue:
                highestCorrelationValue = treatment_correlations[treatment2_column]
                highestCorrelationKey = treatment2_column
    #print highestCorrelationKey
    #print highestCorrelationValue
    return highestCorrelationValue,highestCorrelationKey

#get a list of all the conditions this user has
#we will search each of them to see which one is most actionable
conditions = list(set(test_df['condition']))

#I'm just taking the highest and lowest predicted effectiveness for all conditions, could just as easily do this per condition
highestPredictedValue = 0 
highestPredictedKey = ""
highestPredictedCondition = ""
lowestPredictedValue = 0
lowestPredictedKey = ""
lowestPredictedCondition = ""
for condition in conditions:
    condition_rows = test_df[test_df['condition'] == condition]
    correlations = pd.read_csv(modeldir + '/' + condition.replace('/', '').replace("\n","").replace("\r","") + "_" + distance_metric + ".csv")
    find_closest_func = functools.partial(find_closest,correlations) #this is so I can pass an argument into my transform function
    print condition_rows['treatment']
    condition_rows['closest_correlation_value'] = condition_rows.groupby('user_id')['treatment'].transform(find_closest_func)

    predicted_value = condition_rows[condition_rows['treatment'] == corr_key]['effectiveness'].values[0]
    if highestPredictedValue < predicted_value:
        highestPredictedValue = predicted_value
        highestPredictedKey = corr_key
        highestPredictedCondition = condition
    if lowestPredictedValue > predicted_value:
        lowestPredictedValue = predicted_value
        lowestPredictedKey = corr_key
        lowestPredictedCondition = condition

if highestPredictedValue > 0:
    print "This user may have good results treating " + highestPredictedCondition + " with " + highestPredictedKey
if lowestPredictedValue < 0:
    print "This user may have good results treating " + lowestPredictedCondition + " by staying away from " + lowestPredictedKey