from src.datagen import generate_person_ids, generate_person_table, generate_visit_table, generate_condition_table, generate_measurement_table, generate_drug_exposure_table
import pandas as pd

n_persons = 10000
n_visits = 50000
export_dir = 'export'

# person
person_ids = generate_person_ids(n_persons)
person_df = generate_person_table(person_ids)
print("persons generated...")

# visit_occurrence
visit_df = generate_visit_table(person_ids, n_visits)
print("visits generated...")

# condition_occurrence
condition_df = generate_condition_table(person_ids, visit_df)
print("conditions generated...")

# drug_exposure
drug_df = generate_drug_exposure_table(person_ids, visit_df)
print("drugs generated...")

# measurement
measurement_df = generate_measurement_table(person_ids, visit_df)
print("measurements generated...")

# export
print("exporting OMOP tables...")

tables = {
    'person': person_df,
    'visit_occurrence': visit_df,
    'condition_occurrence': condition_df,
    'drug_exposure': drug_df,
    'measurement': measurement_df
}

# reordering and checking for column existence
# can replace with dataclasses
TABLE_COLUMNS = {
    'person': [
        'person_id', 'gender_concept_id', 'year_of_birth', 'month_of_birth',
        'day_of_birth', 'birth_datetime', 'race_concept_id', 'ethnicity_concept_id',
        'location_id', 'provider_id', 'care_site_id', 'person_source_value',
        'gender_source_value', 'gender_source_concept_id', 'race_source_value',
        'race_source_concept_id', 'ethnicity_source_value', 'ethnicity_source_concept_id'
    ],
    
    'visit_occurrence': [
        'visit_occurrence_id', 'person_id', 'visit_concept_id', 'visit_start_date',
        'visit_start_datetime', 'visit_end_date', 'visit_end_datetime', 'visit_type_concept_id',
        'provider_id', 'care_site_id', 'visit_source_value', 'visit_source_concept_id',
        'admitted_from_concept_id', 'admitted_from_source_value', 'discharged_to_concept_id',
        'discharged_to_source_value', 'preceding_visit_occurrence_id'
    ],
    
    'condition_occurrence': [
        'condition_occurrence_id', 'person_id', 'condition_concept_id', 'condition_start_date',
        'condition_start_datetime', 'condition_end_date', 'condition_end_datetime',
        'condition_type_concept_id', 'condition_status_concept_id', 'stop_reason',
        'provider_id', 'visit_occurrence_id', 'visit_detail_id', 'condition_source_value',
        'condition_source_concept_id', 'condition_status_source_value'
    ],
    
    'drug_exposure': [
        'drug_exposure_id', 'person_id', 'drug_concept_id', 'drug_exposure_start_date',
        'drug_exposure_start_datetime', 'drug_exposure_end_date', 'drug_exposure_end_datetime',
        'verbatim_end_date', 'drug_type_concept_id', 'stop_reason', 'refills', 'quantity',
        'days_supply', 'sig', 'route_concept_id', 'lot_number', 'provider_id',
        'visit_occurrence_id', 'visit_detail_id', 'drug_source_value',
        'drug_source_concept_id', 'route_source_value', 'dose_unit_source_value'
    ],
    
    'measurement': [
        'measurement_id', 'person_id', 'measurement_concept_id', 'measurement_date',
        'measurement_datetime', 'measurement_time', 'measurement_type_concept_id',
        'operator_concept_id', 'value_as_number', 'value_as_concept_id', 'unit_concept_id',
        'range_low', 'range_high', 'provider_id', 'visit_occurrence_id', 'visit_detail_id',
        'measurement_source_value', 'measurement_source_concept_id', 'unit_source_value',
        'unit_source_concept_id', 'value_source_value', 'measurement_event_id',
        'meas_event_field_concept_id'
    ]
}

for table_name, df in tables.items():
    df.to_csv(
        f"export/{table_name}.csv",
        index=False,
        columns=TABLE_COLUMNS[table_name]
    )

print("OMOP tables exported.")