-- Extract FHIR bundles to relational tables for readmission detection
-- This creates raw_encounters and raw_patients from fhir_bundles JSON

-- Drop existing tables
DROP TABLE IF EXISTS raw_encounters CASCADE;
DROP TABLE IF EXISTS raw_patients CASCADE;

-- Create raw_patients table
CREATE TABLE raw_patients AS
WITH patient_resources AS (
    SELECT 
        patient_id,
        jsonb_array_elements(bundle_data::jsonb->'entry') as entry
    FROM fhir_bundles
)
SELECT DISTINCT
    patient_id as id,
    (entry->'resource'->>'birthDate')::date as birthdate,
    entry->'resource'->>'gender' as gender,
    COALESCE(
        entry->'resource'->'extension'->0->'extension'->0->>'valueString',
        'unknown'
    ) as race
FROM patient_resources
WHERE entry->'resource'->>'resourceType' = 'Patient';

CREATE INDEX idx_raw_patients_id ON raw_patients(id);

-- Create raw_encounters table
CREATE TABLE raw_encounters AS
WITH encounter_resources AS (
    SELECT 
        patient_id,
        jsonb_array_elements(bundle_data::jsonb->'entry') as entry
    FROM fhir_bundles
)
SELECT 
    entry->'resource'->>'id' as id,
    patient_id,
    (entry->'resource'->'period'->>'start')::timestamp as start_date,
    (entry->'resource'->'period'->>'end')::timestamp as stop_date,
    LOWER(entry->'resource'->>'class') as encounterclass
FROM encounter_resources
WHERE entry->'resource'->>'resourceType' = 'Encounter'
AND entry->'resource'->'period'->>'start' IS NOT NULL
AND entry->'resource'->'period'->>'end' IS NOT NULL;

CREATE INDEX idx_raw_encounters_patient ON raw_encounters(patient_id);
CREATE INDEX idx_raw_encounters_class ON raw_encounters(encounterclass);

-- Verify data
SELECT 'Patients loaded:' as info, COUNT(*) as count FROM raw_patients
UNION ALL
SELECT 'Encounters loaded:', COUNT(*) FROM raw_encounters
UNION ALL
SELECT 'Inpatient encounters:', COUNT(*) FROM raw_encounters WHERE encounterclass LIKE '%inpatient%';
