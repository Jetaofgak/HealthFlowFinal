-- ============================================================================
-- POPULATE MICROSERVICE TABLES FROM DATASET_FINAL
-- ============================================================================
-- This script populates patient_features and risk_predictions tables
-- from the existing dataset_final table to make the dashboard work
-- ============================================================================

\echo '=== Populating patient_features from dataset_final ==='

-- Truncate existing data
TRUNCATE TABLE patient_features CASCADE;

-- Insert patient features from dataset_final
INSERT INTO patient_features (
    patient_id,
    age,
    gender,
    bmi,
    avg_systolic_bp,
    avg_diastolic_bp,
    avg_heart_rate,
    height_cm,
    weight_kg,
    avg_cholesterol,
    avg_hdl,
    avg_ldl,
    avg_triglycerides,
    avg_hemoglobin,
    total_observations,
    observation_span_days,
    consultation_frequency,
    features_json,
    extraction_date
)
SELECT
    patient_id,
    age,
    CASE
        WHEN gender_male = 1 THEN 'male'
        WHEN gender_female = 1 THEN 'female'
        ELSE 'unknown'
    END as gender,
    vit_bmi as bmi,
    vit_sys_bp as avg_systolic_bp,
    vit_dia_bp as avg_diastolic_bp,
    vit_heart_rate as avg_heart_rate,
    vit_height as height_cm,
    vit_weight as weight_kg,
    lab_cholesterol as avg_cholesterol,
    lab_hdl as avg_hdl,
    lab_ldl as avg_ldl,
    NULL as avg_triglycerides,  -- Not in dataset
    NULL as avg_hemoglobin,     -- Not in dataset
    NULL as total_observations,
    NULL as observation_span_days,
    NULL as consultation_frequency,
    jsonb_build_object(
        'age', age,
        'bmi', vit_bmi,
        'num_conditions', num_conditions,
        'num_medications', num_medications,
        'has_diabetes', cond_diabetes,
        'has_hypertension', cond_hypertension,
        'has_chf', cond_chf,
        'readmission_label', label_readmission
    ) as features_json,
    NOW() as extraction_date
FROM dataset_final;

\echo '=== Populating risk_predictions from dataset_final ==='

-- Truncate existing data
TRUNCATE TABLE risk_predictions CASCADE;

-- Insert basic risk predictions using actual readmission labels
INSERT INTO risk_predictions (
    patient_id,
    framingham_score,
    ascvd_10year_risk,
    risk_category,
    risk_factors,
    recommendations
)
SELECT
    patient_id,
    CASE
        WHEN label_readmission = 1 THEN num_conditions * 0.5 + age * 0.3
        ELSE num_conditions * 0.3 + age * 0.2
    END::float as framingham_score,
    CASE
        WHEN label_readmission = 1 THEN (num_medications * 1.5 + num_conditions) / 10.0
        ELSE (num_medications * 0.8 + num_conditions * 0.5) / 10.0
    END::float as ascvd_10year_risk,
    CASE
        WHEN label_readmission = 1 AND (num_conditions > 50 OR num_medications > 60) THEN 'high'
        WHEN label_readmission = 1 OR num_conditions > 30 THEN 'medium'
        ELSE 'low'
    END as risk_category,
    jsonb_build_array(
        CASE WHEN cond_diabetes = 1 THEN 'Diabetes' END,
        CASE WHEN cond_hypertension = 1 THEN 'Hypertension' END,
        CASE WHEN cond_chf = 1 THEN 'Congestive Heart Failure' END,
        CASE WHEN polypharmacy = 1 THEN 'Polypharmacy' END,
        CASE WHEN age > 65 THEN 'Advanced Age' END
    ) - 'null'::jsonb as risk_factors,
    jsonb_build_array(
        'Regular monitoring recommended',
        'Follow medication regimen',
        'Lifestyle modifications advised'
    ) as recommendations
FROM dataset_final;

\echo '=== ✅ Population Complete ==='

-- Verify counts
\echo '=== Verification ==='
SELECT 'patient_features' as table_name, COUNT(*) as row_count FROM patient_features
UNION ALL
SELECT 'risk_predictions' as table_name, COUNT(*) as row_count FROM risk_predictions;

-- Show sample stats
\echo '=== Sample Statistics ==='
SELECT
    COUNT(*) as total_patients,
    AVG(age)::numeric(10,1) as avg_age,
    AVG(bmi)::numeric(10,2) as avg_bmi,
    AVG(avg_cholesterol)::numeric(10,2) as avg_cholesterol
FROM patient_features;

SELECT
    risk_category,
    COUNT(*) as count_by_category
FROM risk_predictions
GROUP BY risk_category
ORDER BY risk_category;
