# References
https://www.youtube.com/watch?v=i9RX03zFDHU&list=PLxSYMfvSdovUHUAvTsKENaQBIX724g6l4
https://alembic.sqlalchemy.org/en/latest/autogenerate.html

# Initialize alembic
alembic init alembic

# Create a revision
alembic revision -m "Create user Table"

# run the latest revision
alembic upgrade head

# run a particular revision using the revision id
alembic upgrade 9157f389ea3c

# shows the latest revision that has been applied
alembic current

# relative downgrade; downgrade to the previous revision from the current one
alembic downgrade -1

# relative upgrade; upgrade to the next revision from the current one
alembic upgrade +1

# revert back to the original state of the dataabse
alembic downgrade base

# Autogenerate revisions from the models
## Note: You need to modifu the env.py file under the alembic folder and set the target_metadata
alembic revision --autogenerate -m "Added Company model"