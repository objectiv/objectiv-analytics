SELECT DISTINCT feature_hash,
                stack_selection as feature_name,
                'Pretty' || stack_selection as feature_pretty_name
-- TODO, get this from a variable to use dynamic feature selection
FROM {{ ref('hashed_features') }}
