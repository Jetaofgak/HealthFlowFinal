-- Detect readmissions from raw_encounters table
-- Uses LEAD() window function to find next admission within 30 days

DROP TABLE IF EXISTS patient_readmissions;

CREATE TABLE patient_readmissions AS
WITH base_encounters AS (
    SELECT 
        e.id AS encounter_id,
        e.patient_id,
        e.start_date,
        e.stop_date,
        p.birthdate,
        p.gender,
        p.race,
        -- Calculate next admission for this patient
        LEAD(e.start_date) OVER (PARTITION BY e.patient_id ORDER BY e.start_date) AS next_admission
    FROM raw_encounters e
    JOIN raw_patients p ON e.patient_id = p.id
    WHERE e.encounterclass::jsonb->>'code' IN ('imp', 'emer')  -- inpatient or emergency
)
SELECT 
    encounter_id,
    patient_id,
    start_date,
    stop_date,
    EXTRACT(YEAR FROM age(start_date, birthdate)) AS age,
    CASE WHEN gender = 'male' THEN 1 ELSE 0 END AS gender_male,
    CASE WHEN race LIKE '%white%' THEN 1 ELSE 0 END AS race_white,
    CASE WHEN race LIKE '%black%' THEN 1 ELSE 0 END AS race_black,
    -- Readmission label: 1 if next admission within 30 days
    CASE 
        WHEN next_admission IS NOT NULL 
             AND (next_admission - stop_date) <= INTERVAL '30 days' THEN 1 
        ELSE 0 
    END AS label_readmission,
    EXTRACT(days FROM (next_admission - stop_date)) as days_to_next_admission
FROM base_encounters;

CREATE INDEX idx_readmissions_patient ON patient_readmissions(patient_id);

-- Statistics
SELECT 
    'Total encounters' as metric,
    COUNT(*)::text as value
FROM patient_readmissions
UNION ALL
SELECT 
    'Readmissions (30d)',
    COUNT(*)::text
FROM patient_readmissions
WHERE label_readmission = 1
UNION ALL
SELECT 
    'Readmission rate',
    ROUND(100.0 * SUM(label_readmission) / COUNT(*), 2)::text || '%'
FROM patient_readmissions;
