# NFL Pipeline Backend

The pipeline currently exists as a python module. The module executes jobs as functions sequentially. This solution will not scale well and will be modified when needed or time permits, but this minimal solution works for a simple pipeline like this one.

## Running the Pipeline

- To run pipeline, use the make target `make run-pipeline`, which under the hood runs the `pipeline` module with `python3 -m pipeline`.

## Adding a New Job to the Pipeline

- Create a new python script with the job. The convention is for the job scripts to have a single public method, `run()` that is called during execution of the pipeline.
- If the job uses `nflscrapr`, create a corresponding job in `/nflscrapr` using the exiting ones as templates. The only thing required is updating the arguments and the name of the function to call.
- If a new table is required, follow the instructions below for creating a new table.
- Add the job to the pipeline in `__main__.py` by importing it and calling its `.run()` method. The job must be in the proper sequence with the existing jobs.

## Modifying the Database Schema

Alembic is used to manage dataase schemas, with SQLAlchemy used as an ORM. All schemas are defined in `models.py`, and alemic uses these models to automatically update the database schema.

To create or modify a table:

#### Models
- For a new table, add a new class in `models.py`
- To modify a table, make changes to the existing class definition in `models.py`

#### Alembic
- Alembic will automatic generate the revision for you by comparing the class definitions in `models.py` with the actual database schema
- To autogenerate the revision, run:
```
make auto-revision message="revision_message_here"
```
- This will create the revision file in `/alembic/versions`
- To apply the revision to the database, run:
```
make migrate
```
- If you need to undo the migration, shell into the app and downgrade:
```
your computer > make db-shell
inside shell  > alembic downgrade -1 
```
- You may delete the revision file if necessary