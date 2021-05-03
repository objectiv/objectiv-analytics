This is a dbt project.

to prepare dbt env:
```bash
mkdir -p ~/.dbt
cp profiles_template.yml ~/.dbt/profiles.yml
[ edit that file, add proper credentials]

# check that all is good
dbt debug
```

to run the models:
```bash
dbt run
```

### Resources:
- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](http://slack.getdbt.com/) on Slack for live discussions and support
- Find [dbt events](https://events.getdbt.com) near you
- Check out [the blog](https://blog.getdbt.com/) for the latest news on dbt's development and best practices
