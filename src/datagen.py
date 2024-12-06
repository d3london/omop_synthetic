import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats

"""
Functions to generate synthetic data for core OMOP CDM 5.4 Tables
    DONE - person, visit_occurrence, condition_occurrence, drug_occurrence, measurements
    TO DO - refactor, add names to X_source_value for readability, add observation (deprivation), death, use dataclasses
Some basic clinical sense is maintained, although dataset generation does not aim to preserve true-to-life distributions
"""

def generate_person_ids(n):
    """
    Generate list of unique person_id where n = no of patients in dataset
    """
    return list(range(1000000000, n + 1000000000))

def generate_person_table(person_ids):
    """
    Generate OMOP person table
    """
    n = len(person_ids)
    current_year = datetime.now().year

    # define distributions for each demographic
    gender_dist = {
        8507: 0.5,  # M | MALE
        8532: 0.5   # F | FEMALE
    }
    race_dist = {
        8527: 0.70,     # 5 | White
        8516: 0.10,     # 3 | Black of African American
        8515: 0.10,     # 2 | Asian
        38003579: 0.10	# 2.06 | Chinese
    }
    ethnicity_dist = {
        38003564: 1.0,    # Not Hispanic
        38003563: 0.0     # Hispanic
    }
    
    # generate age dist with left skew (more elderly)
    # test skew here: https://homepage.divms.uiowa.edu/~mbognar/applets/beta.html
    age_range = (18, 88)
    alpha, beta = 6, 2
    age_dist = stats.beta.rvs(alpha, beta, size=n) # distribution from 0 to 1
    ages = age_dist * (age_range[1] - age_range[0]) + age_range[0] # standardise
    birth_years = current_year - ages.astype(int)
    
    # create omop.person dataframe
    df = pd.DataFrame({
        'person_id': person_ids,
        'gender_concept_id': np.random.choice( 
            list(gender_dist.keys()),
            n,
            p=list(gender_dist.values()) ## proba to assign variable
        ),
        'year_of_birth': birth_years,
        'race_concept_id': np.random.choice(
            list(race_dist.keys()),
            n,
            p=list(race_dist.values())
        ),
        'ethnicity_concept_id': np.random.choice(
            list(ethnicity_dist.keys()),
            n,
            p=list(ethnicity_dist.values())
        )
    })
    # other columns
    df['month_of_birth'] = None
    df['day_of_birth'] = None
    df['birth_datetime'] = None
    df['location_id'] = None
    df['provider_id'] = None
    df['care_site_id'] = None
    df['person_source_value'] = None
    df['gender_source_value'] = None
    df['gender_source_concept_id'] = None
    df['race_source_value'] = None
    df['race_source_concept_id'] = None
    df['ethnicity_source_value'] = None
    df['ethnicity_source_concept_id'] = None

    return df

def generate_visit_table(person_ids, n_visits):
    """
    Generate OMOP visit_occurrence table
    """    
    visit_ids = list(range(1000000000, n_visits + 1000000000))
    start_date = pd.Timestamp('2015-01-01')
    end_date = pd.Timestamp('2023-12-31')
    date_range = (end_date - start_date).days

    visit_types = {
        9201: 0.3,     # IP | Inpatient Visit
        9202: 0.7      # OP | Outpatient Visit
    }
    
    # assign person_ids to sequential visits
    # can look at a more realistic way to do person -> visit mapping down the line
    assigned_person_ids = np.random.choice(person_ids, n_visits)
    
    visit_concepts = np.random.choice(
        list(visit_types.keys()),
        n_visits,
        p=list(visit_types.values())
    )
    
    # random offset from start date to create visit dates  
    start_offsets = np.random.randint(0, date_range, n_visits)
    visit_start_dates = [start_date + pd.Timedelta(days=int(offset)) for offset in start_offsets]
    
    # end dates based on visit type
    visit_end_dates = []
    for i in range(n_visits):
        if visit_concepts[i] == 9201:  # IP | Inpatient Visit
            length = np.random.randint(1, 15)
            visit_end_dates.append(visit_start_dates[i] + pd.Timedelta(days=length))
        else:
            visit_end_dates.append(visit_start_dates[i]) # OP end on same day
    
    # create omop.visit_occurrence dataframe
    df = pd.DataFrame({
        'visit_occurrence_id': visit_ids,
        'person_id': assigned_person_ids,
        'visit_concept_id': visit_concepts,
        'visit_start_date': visit_start_dates,
        'visit_end_date': visit_end_dates,
        'visit_type_concept_id': 44818517  # Visit derived from encounter on claim (i.e. CDS)
    })
    df['visit_start_datetime'] = None
    df['visit_end_datetime'] = None
    df['provider_id'] = None
    df['care_site_id'] = None
    df['visit_source_value'] = None
    df['visit_source_concept_id'] = None
    df['admitted_from_concept_id'] = None
    df['admitted_from_source_value'] = None
    df['discharged_to_concept_id'] = None
    df['discharged_to_source_value'] = None
    df['preceding_visit_occurrence_id'] = None

    return df

def generate_condition_table(person_ids, visit_df):
    """
    Generate OMOP condition_occurrence table
    """    
    # define clusters of conditions and their distributions within clusters
    # keeping these hard coded for simplicity, but would push all to a definitions file down the line
    CONDITION_CLUSTERS = {
        "cardiometabolic": {
            316866: 0.30,  # Hypertensive disorder
            201820: 0.20,  # Diabetes mellitus
            321588: 0.15,  # Heart disease
            381591: 0.15,  # Cerebrovascular disease
            434376: 0.10,  # Acute MI
            321052: 0.10   # Peripheral vascular disease
        },
        "respiratory": {
            255848: 0.30,  # Pneumonia
            255573: 0.25,  # Chronic obstructive lung disease
            260139: 0.20,  # Acute bronchitis
            256449: 0.15,  # Bronchiectasis
            261880: 0.10   # Atelectasis
        },
        "musculoskeletal": {
            80180: 0.30,   # Osteoarthritis
            80809: 0.25,   # Rheumatoid arthritis
            4046660: 0.20, # Chronic back pain
            4291025: 0.15, # Inflammatory arthritis
            4000634: 0.10  # Acute arthritis
        },
        "gastrointestinal": {
            4027663: 0.30,  # Peptic ulcer
            40398568: 0.20,  # Duodenal ulcer
            201340: 0.20,  # Gastritis
            4074815: 0.15,  # Inflammatory bowel disease
            45470366: 0.15  # Oesophagitis
        },
        "mental_health": {
            4152280: 0.30,  # Major depressive disorder
            434613: 0.25,  # Generalized anxiety disorder
            40388256: 0.20,  # Bipolar disorder
            435783: 0.15,  # Schizophrenia
            40388323: 0.10   # Post-traumatic stress disorder
        }
    }
    # define distributions of clusters
    CLUSTER_DISTRIBUTION = {
        "cardiometabolic": 0.25,
        "respiratory": 0.20,
        "musculoskeletal": 0.20,
        "gastrointestinal": 0.20,
        "mental_health": 0.15
    }

    # assign clusters to persons / visits / dates
    # for simplicity, each person only gets assigned a single disease cluster
    person_cluster_map = {}
    for person_id in person_ids:

        # give each person a cluster based on the distribution
        assigned_cluster = np.random.choice(
            list(CLUSTER_DISTRIBUTION.keys()),
            p=list(CLUSTER_DISTRIBUTION.values())
        )
        
        # create dict of person/visits and start date
        person_visits = visit_df[visit_df['person_id'] == person_id].copy()
        visit_info = person_visits[['visit_occurrence_id', 'visit_start_date']].to_dict('records')
        
        # create dict of person/cluster/visits/visit dates
        person_cluster_map[person_id] = {
            'cluster': assigned_cluster,
            'visits': visit_info
        }
    
    # assign conditions from each cluster to person/visit
    condition_records = []
    condition_id = 1000000000
    for person_id, info in person_cluster_map.items():

        # pull out cluster data
        cluster = info['cluster']
        cluster_concepts = CONDITION_CLUSTERS[cluster]
        
        # for each visit, assign 1 to 3 assoc conditions
        for visit in info['visits']:
            n_conditions = np.random.randint(1, 4)
            
            # keep to the assigned cluster
            selected_conditions = np.random.choice(
                list(cluster_concepts.keys()),
                size=n_conditions,
                p=list(cluster_concepts.values())
            )
            
            # create record per condition, attach visit/date
            for condition in selected_conditions:
                condition_records.append({
                    'condition_occurrence_id': condition_id,
                    'person_id': person_id,
                    'condition_concept_id': condition,
                    'condition_start_date': visit['visit_start_date'],
                    'condition_start_datetime': None,
                    'condition_end_date': None,
                    'condition_end_datetime': None,
                    'condition_type_concept_id': 32020, # EHR encounter diagnosis
                    'condition_status_concept_id': None,
                    'stop_reason': None,
                    'provider_id': None,
                    'visit_occurrence_id': visit['visit_occurrence_id'],
                    'visit_detail_id': None,
                    'condition_source_value': None,
                    'condition_source_concept_id': None,
                    'condition_status_source_value': None
                })
                condition_id += 1
    
    df = pd.DataFrame.from_records(condition_records)
    
    return df

def generate_drug_exposure_table(person_ids, visit_df):
    """
    Generate OMOP drug_exposure table
    """    
    # clusters of drugs that match conditions above
    DRUG_CLUSTERS = {
        "cardiometabolic": {
            1112807: 0.35,  # Aspirin
            1503297: 0.35,  # Metformin
            1545958: 0.30   # Atorvastatin
        },
        "respiratory": {
            1154343: 0.40,  # Albuterol / Salbutamol
            1550557: 0.35,  # Prednisolone
            1154161: 0.25   # Montelukast
        },
        "musculoskeletal": {
            1201620: 0.30,  # Codeine
            1115008: 0.55,  # Naproxen
            1110410: 0.15   # Morphine
        },
        "gastrointestinal": {
            948078: 0.65,   # Pantoprazole
            961047: 0.35    # Ranitidine
        },
        "mental_health": {
            739138: 0.40,   # Sertraline
            1153013: 0.35,  # Promethazine
            19124477: 0.25  # Lithium
        }
    }
    
    # keep same distributions
    DRUG_CLUSTER_DISTRIBUTION = {
        "cardiometabolic": 0.25,
        "respiratory": 0.20,
        "musculoskeletal": 0.20,
        "gastrointestinal": 0.20,
        "mental_health": 0.15
    }

    # mapping of persons to drug cluster and visits
    person_cluster_map = {}
    for person_id in person_ids:
        assigned_cluster = np.random.choice(
            list(DRUG_CLUSTER_DISTRIBUTION.keys()),
            p=list(DRUG_CLUSTER_DISTRIBUTION.values())
        )
        
        person_visits = visit_df[visit_df['person_id'] == person_id].copy()
        visit_info = person_visits[['visit_occurrence_id', 'visit_start_date']].to_dict('records')
        
        person_cluster_map[person_id] = {
            'cluster': assigned_cluster,
            'visits': visit_info
        }
    
    drug_records = []
    drug_exposure_id = 1000000000
    
    for person_id, info in person_cluster_map.items():
        cluster = info['cluster']
        cluster_concepts = DRUG_CLUSTERS[cluster]
        
        for visit in info['visits']:
            n_drugs = np.random.randint(1, 3)  # 1-2 drugs per visit
            
            # Keep to the assigned cluster
            selected_drugs = np.random.choice(
                list(cluster_concepts.keys()),
                size=n_drugs,
                p=list(cluster_concepts.values())
            )
            
            for drug in selected_drugs:
                drug_records.append({
                    'drug_exposure_id': drug_exposure_id,
                    'person_id': person_id,
                    'drug_concept_id': drug,
                    'drug_exposure_start_date': visit['visit_start_date'],
                    'drug_exposure_start_datetime': None,
                    'drug_exposure_end_date': visit['visit_start_date'],
                    'drug_exposure_end_datetime': None,
                    'verbatim_end_date': None,
                    'drug_type_concept_id': 38000177,  # Prescription written
                    'stop_reason': None,
                    'refills': None,
                    'quantity': None,
                    'days_supply': None,
                    'sig': None,
                    'route_concept_id': 4132161,  # Oral
                    'lot_number': None,
                    'provider_id': None,
                    'visit_occurrence_id': visit['visit_occurrence_id'],
                    'visit_detail_id': None,
                    'drug_source_value': None,
                    'drug_source_concept_id': None,
                    'route_source_value': None,
                    'dose_unit_source_value': None
                })
                drug_exposure_id += 1
    
    df = pd.DataFrame.from_records(drug_records)
    
    return df

def generate_measurement_table(person_ids, visit_df):
    """
    Generate OMOP measurement table with common clinical measurements
    """
    # Define common measurements and their normal ranges/distributions
    MEASUREMENTS = {
        "Hemoglobin": {
            "concept_id": 3000963,
            "unit_concept_id": 8713,  # gram per deciliter
            "mean": 12,
            "std": 1.5,
            "probability": 0.8  # chance of having measured
        },
        "Creatinine": {
            "concept_id": 3032033,
            "unit_concept_id": 8749,  # micromole per liter
            "mean": 70,
            "std": 30,
            "probability": 0.6
        },
        "BMI": {
            "concept_id": 3038553,
            "unit_concept_id": 9531,  # kilogram per m^2
            "mean": 27.0,
            "std": 5.0,
            "probability": 0.9
        },
        "Systolic Blood Pressure": {
            "concept_id": 3004249,
            "unit_concept_id": 8876,  # mmHg
            "mean": 130,
            "std": 25,
            "probability": 0.9
        }
    }

    measurement_records = []
    measurement_id = 1000000000

    for person_id in person_ids:
        person_visits = visit_df[visit_df['person_id'] == person_id]
        
        for _, visit in person_visits.iterrows():
            for measure_name, measure_info in MEASUREMENTS.items():
                
                if np.random.random() < measure_info["probability"]:
                    value = round(np.random.normal(
                        measure_info["mean"],
                        measure_info["std"]
                    ), 0)
                    
                    measurement_records.append({
                        'measurement_id': measurement_id,
                        'person_id': person_id,
                        'measurement_concept_id': measure_info["concept_id"],
                        'measurement_date': visit['visit_start_date'],
                        'measurement_datetime': None,
                        'measurement_time': None,
                        'measurement_type_concept_id': 44818701,  # Lab result
                        'operator_concept_id': None,
                        'value_as_number': value,
                        'value_as_concept_id': None,
                        'unit_concept_id': measure_info["unit_concept_id"],
                        'range_low': None,
                        'range_high': None,
                        'provider_id': None,
                        'visit_occurrence_id': visit['visit_occurrence_id'],
                        'visit_detail_id': None,
                        'measurement_source_value': None,
                        'measurement_source_concept_id': None,
                        'unit_source_value': None,
                        'value_source_value': None,
                        'unit_source_concept_id': None,
                        'measurement_event_id': None,
                        'meas_event_field_concept_id': None
                    })
                    measurement_id += 1

    df = pd.DataFrame.from_records(measurement_records)
   
    return df