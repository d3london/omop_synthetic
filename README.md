# Generating simple synthetic OMOP CDM 5.4 tables

>[!IMPORTANT]
>This is a simple script to generate core OMOP tables with minimum levels of synthetic (fake) data, without any view towards realism.
>It is designed to support development of query and visualisation functionality, not for analysis.
>It is only populated with a small number of concept types (hardcoded in src/datagen.py) which are generated with a minimum level of clinical realism. 

To use:

1. Configure cohort size and number of visits in `create_synthetic_omop.py`

2. Generate data: `python create_synthetic_omop.py`

3. Validate OMOP constraints: `duckdb -init validate_omop.sql`. You will need to install the [duckdb cli](https://duckdb.org/docs/api/cli/overview.html) for this. If OMOP compatible, you should receive row counts for each table. Note that this does not yet validate against the vocabulary table. 
