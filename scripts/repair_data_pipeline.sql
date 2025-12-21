-- ============================================================================
-- REPAIR DATA PIPELINE: Populate fhir_resources from fhir_bundles
-- ============================================================================
-- The DeID service expects data in 'fhir_resources', but the loader 
-- only populated 'fhir_bundles' and 'raw_*' tables.
-- This script unpacks the bundles into individual resources.

\echo '=== Populating fhir_resources from fhir_bundles ==='

INSERT INTO fhir_resources (fhir_id, resource_type, resource_data, sync_date)
SELECT 
    entry->'resource'->>'id' as fhir_id,
    entry->'resource'->>'resourceType' as resource_type,
    entry->'resource' as resource_data,
    NOW() as sync_date
FROM (
    -- Extract all entries from all bundles
    SELECT jsonb_array_elements(bundle_data->'entry') as entry
    FROM fhir_bundles
) extracted
WHERE 
    entry->'resource'->>'resourceType' IS NOT NULL
    AND entry->'resource'->>'id' IS NOT NULL
ON CONFLICT (fhir_id) DO NOTHING;

\echo '=== ✅ Migration Complete ==='

-- Verify counts
SELECT resource_type, COUNT(*) as count 
FROM fhir_resources 
GROUP BY resource_type 
ORDER BY count DESC;
