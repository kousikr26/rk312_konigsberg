import pandas as pd
import numpy as np 
from functools import reduce



def SumFeatures(df, pivot_identifier, SD_dict):
	"""
	Returns : A dataframe with features as in SD_dict with sum of all the instances in the dataframe for the features in SD_dict along all pivot identifiers.
			  The index of the dataframe are the uniqe numbers present in the whole dataframe.
	"""


	def UpdateFunc(row_df):

		for pivot in (pivot_identifier):
			for feature in SD_dict.keys():
				new_df.loc[row_df[pivot]][feature] += row_df[feature]


	copy_df = df.drop([df.columns[i] for i in range(len(df.columns)) if df.columns[i] not in pivot_identifier + list(SD_dict.keys())], axis = 1).copy(deep=True)

	unique_instances = reduce(np.union1d, (*[copy_df[pivot_identifier[i]].unique() for i in range(len(pivot_identifier))]))

	new_df = pd.DataFrame(index =unique_instances, columns = list(SD_dict.keys()), data=0.0)

	copy_df.apply(UpdateFunc, axis=1)

	return new_df



def StatisticalAnomalyFinder(df, pivot_identifier, SD_dict): 
	"""
	Finds Statistical Anomaly in a Pandas dataframe.

	Assumptions :: 
					1. All Features in SD_dict corresponds to Numerical features of the dataframe df.
					2. There can be multiple entries of the same name/object in features of pivot_identifier.

	df : Dataframe from where the anomalies will be calculated from.

	pivot_identifier : The list of feature name(s) of the df whose rows are supposed to indicate new data of an instance.
						If len(pivot_identifier) > 1, it is assumed that the unique identifier is contained in each of these features.
						Example, 'Name' in a school register or ['Caller', 'Reciever'] in a CDR data.

	SD_dict : A dict of standard deviations, where dict's keys will be the feature name of the df of whom to find the anomalies from.
				 


	Returns : 
				1. Results_dict : A dict of Series objects for each feature passed in SD_dict.
				2. p_values : The tolerance limit \mu + \alpha * \sigma for each feature in SD_dict, \alpha is the standard deviation 
							 as passed as values in SD_dict.
	"""

	new_df = SumFeatures(df, pivot_identifier, SD_dict)

	alpha = list(SD_dict.values())

	p_values = new_df.mean() + alpha * new_df.std()
	#Series object with p_values of each feature in order as in SD_dict

	Results_dict = dict.fromkeys(SD_dict)

	for feature in SD_dict.keys():
		Results_dict[feature] = new_df.loc[new_df[feature] > p_values[feature]][feature].copy()

	return Results_dict, p_values
