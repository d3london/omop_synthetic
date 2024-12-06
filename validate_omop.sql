-- duckdb -init validate_omop.sql
-- (1) Create OMOP tables
-- (2) Load CSV files
-- (3) Run validation checks
-- (4) Clean up

-- create OMOP tables
create or replace table person (
    person_id integer not null primary key,
    gender_concept_id integer not null,
    year_of_birth integer not null,
    month_of_birth integer,
    day_of_birth integer,
    birth_datetime timestamp,
    race_concept_id integer not null,
    ethnicity_concept_id integer not null,
    location_id integer,
    provider_id integer,
    care_site_id integer,
    person_source_value varchar(50),
    gender_source_value varchar(50),
    gender_source_concept_id integer,
    race_source_value varchar(50),
    race_source_concept_id integer,
    ethnicity_source_value varchar(50),
    ethnicity_source_concept_id integer
);

create or replace table visit_occurrence (
    visit_occurrence_id integer not null primary key,
    person_id integer not null references person(person_id),
    visit_concept_id integer not null,
    visit_start_date date not null,
    visit_start_datetime timestamp,
    visit_end_date date not null,
    visit_end_datetime timestamp,
    visit_type_concept_id integer not null,
    provider_id integer,
    care_site_id integer,
    visit_source_value varchar(50),
    visit_source_concept_id integer,
    admitted_from_concept_id integer,
    admitted_from_source_value varchar(50),
    discharged_to_concept_id integer,
    discharged_to_source_value varchar(50),
    preceding_visit_occurrence_id integer
);

create or replace table condition_occurrence (
    condition_occurrence_id integer not null primary key,
    person_id integer not null references person(person_id),
    condition_concept_id integer not null,
    condition_start_date date not null,
    condition_start_datetime timestamp,
    condition_end_date date,
    condition_end_datetime timestamp,
    condition_type_concept_id integer not null,
    condition_status_concept_id integer,
    stop_reason varchar(20),
    provider_id integer,
    visit_occurrence_id integer references visit_occurrence(visit_occurrence_id),
    visit_detail_id integer,
    condition_source_value varchar(50),
    condition_source_concept_id integer,
    condition_status_source_value varchar(50)
);

create or replace table drug_exposure (
    drug_exposure_id integer not null primary key,
    person_id integer not null references person(person_id),
    drug_concept_id integer not null,
    drug_exposure_start_date date not null,
    drug_exposure_start_datetime timestamp,
    drug_exposure_end_date date not null,
    drug_exposure_end_datetime timestamp,
    verbatim_end_date date,
    drug_type_concept_id integer not null,
    stop_reason varchar(20),
    refills integer,
    quantity numeric,
    days_supply integer,
    sig text,
    route_concept_id integer,
    lot_number varchar(50),
    provider_id integer,
    visit_occurrence_id integer references visit_occurrence(visit_occurrence_id),
    visit_detail_id integer,
    drug_source_value varchar(50),
    drug_source_concept_id integer,
    route_source_value varchar(50),
    dose_unit_source_value varchar(50)
);

create or replace table measurement (
    measurement_id integer not null primary key,
    person_id integer not null references person(person_id),
    measurement_concept_id integer not null,
    measurement_date date not null,
    measurement_datetime timestamp,
    measurement_time varchar(10),
    measurement_type_concept_id integer not null,
    operator_concept_id integer,
    value_as_number numeric,
    value_as_concept_id integer,
    unit_concept_id integer,
    range_low numeric,
    range_high numeric,
    provider_id integer,
    visit_occurrence_id integer references visit_occurrence(visit_occurrence_id),
    visit_detail_id integer,
    measurement_source_value varchar(50),
    measurement_source_concept_id integer,
    unit_source_value varchar(50),
    unit_source_concept_id integer,
    value_source_value varchar(50),
    measurement_event_id integer,
    meas_event_field_concept_id integer
);

-- load from CSVs
copy person from 'export/person.csv' (AUTO_DETECT true);
copy visit_occurrence from 'export/visit_occurrence.csv' (AUTO_DETECT true);
copy condition_occurrence from 'export/condition_occurrence.csv' (AUTO_DETECT true);
copy drug_exposure from 'export/drug_exposure.csv' (AUTO_DETECT true);
copy measurement from 'export/measurement.csv' (AUTO_DETECT true);

-- row counts
select 
    'person' as table_name, count(*) as row_count from person
    union all
select 'visit_occurrence', count(*) from visit_occurrence
    union all
select 'condition_occurrence', count(*) from condition_occurrence
    union all
select 'drug_exposure', count(*) from drug_exposure
    union all
select 'measurement', count(*) from measurement;

-- clean up
drop table if exists condition_occurrence;
drop table if exists drug_exposure;
drop table if exists measurement;
drop table if exists visit_occurrence;
drop table if exists person;

.exit