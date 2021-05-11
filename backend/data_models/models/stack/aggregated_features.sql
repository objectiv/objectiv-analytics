SELECT feature_hash, 'aggregator' as feature_name, 'Very Much Aggregation' as feature_pretty_name
-- TODO, get this from a variable to use dynamic feature selection
FROM {{ ref('hashed_features') }}
GROUP BY feature_hash
