import os
os.environ['DSN'] = 'bigquery://objectiv-snowplow-test-2/modelhub_test'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/kathia/Desktop/objectiv/objectiv-analytics/modelhub/.secrets/bach-big-query-testing.json'

# CELL 5
from modelhub import ModelHub
from bach import display_sql_as_markdown
import bach
import pandas as pd
from datetime import timedelta

# CELL 7
# instantiate the model hub and set the default time aggregation to daily
modelhub = ModelHub(time_aggregation='%Y-%m-%d')

# get the Bach DataFrame with Objectiv data
df = modelhub.get_objectiv_dataframe(start_date='2022-02-01')

# CELL 9
# adding specific contexts to the data as columns
df['application'] = df.global_contexts.gc.application
df['root_location'] = df.location_stack.ls.get_from_context_with_type_series(type='RootLocationContext', key='id')

# CELL 11
# model hub: unique users per root location
users_root = modelhub.aggregate.unique_users(df, groupby=['application', 'root_location'])
users_root.head(10)

# CELL 13
# model hub: duration, per root location
duration_root = modelhub.aggregate.session_duration(df, groupby=['application', 'root_location']).sort_index()
duration_root.head(10)

# CELL 15
# how is this time spent distributed?
session_duration = modelhub.aggregate.session_duration(df, groupby='session_id')
# materialization is needed because the expression of the created series contains aggregated data, and it is not allowed to aggregate that.
session_duration = session_duration.materialize()

# show quantiles
session_duration.quantile(q=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]).head(10)

# CELL 18
# set the root locations that we will use based on the definitions above
roots = bach.DataFrame.from_pandas(engine=df.engine,
                                   df=pd.DataFrame({'roots': ['modeling', 'taxonomy', 'tracking', 'home', 'docs']}),
                                   convert_objects=True).roots

# CELL 19
# now we calculate the total time spent per _user_ and create a data frame from it
user_intent_buckets = modelhub.agg.session_duration(df,
                                                    groupby=['user_id'],
                                                    method='sum',
                                                    exclude_bounces=False).to_frame()

# CELL 20
# same as above, but for selected roots only
explore_inform_users_session_duration = modelhub.agg.session_duration((df[(df.root_location.isin(roots)) & (df.application=='objectiv-docs')]),
                                                                      groupby='user_id',
                                                                      method='sum')
# and set it as column
user_intent_buckets['explore_inform_duration'] = explore_inform_users_session_duration

# CELL 21
# first, we set the Inform bucket as a catch-all, meaning users that do not fall into Explore and Implement will be defined as Inform
user_intent_buckets['bucket'] = '1 - inform'

# CELL 22
# calculate buckets duration
user_intent_buckets.loc[(user_intent_buckets.explore_inform_duration >= timedelta(0, 100)) &
                        (user_intent_buckets.explore_inform_duration <= timedelta(0, 690)), 'bucket'] = '2 - explore'

user_intent_buckets.loc[user_intent_buckets.explore_inform_duration > timedelta(0, 690), 'bucket'] = '3 - implement'

# CELL 24
# total number of users per intent bucket
user_intent_buckets.reset_index().groupby('bucket').agg({'user_id': 'nunique'}).head()

# CELL 28
# get the SQL to use this analysis in for example your BI tooling
display_sql_as_markdown(user_intent_buckets)