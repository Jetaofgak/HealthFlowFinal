#!/bin/bash
# Synthea Data Generation Script with Clinical Notes
# This script downloads Synthea and generates synthetic patient data including clinical notes

set -e  # Exit on error

echo "🏥 HealthFlow-MS: Synthea Data Generation"
echo "=========================================="

# Configuration
SYNTHEA_VERSION="master-branch-latest"
SYNTHEA_JAR="synthea-with-dependencies.jar"
SYNTHEA_URL="https://github.com/synthetichealth/synthea/releases/download/${SYNTHEA_VERSION}/${SYNTHEA_JAR}"
NUM_PATIENTS=${1:-1000}  # Default 1000 patients, can override with argument
OUTPUT_DIR="synthea_output"

echo ""
echo "📋 Configuration:"
echo "   Patients to generate: ${NUM_PATIENTS}"
echo "   Output directory: ${OUTPUT_DIR}"
echo ""

# Step 1: Download Synthea if not exists
if [ ! -f "${SYNTHEA_JAR}" ]; then
    echo "📥 Downloading Synthea..."
    wget -q --show-progress "${SYNTHEA_URL}" || curl -L -o "${SYNTHEA_JAR}" "${SYNTHEA_URL}"
    echo "✅ Synthea downloaded"
else
    echo "✅ Synthea already downloaded"
fi

# Step 2: Create output directory
mkdir -p "${OUTPUT_DIR}"

# Step 3: Generate patients with clinical notes
echo ""
echo "🔬 Generating ${NUM_PATIENTS} synthetic patients..."
echo "   This may take several minutes..."
echo ""

java -jar "${SYNTHEA_JAR}" \
    -p ${NUM_PATIENTS} \
    --exporter.fhir.export=true \
    --exporter.clinical_note.export=true \
    --exporter.baseDirectory="${OUTPUT_DIR}" \
    Massachusetts  # State for demographic consistency

echo ""
echo "✅ Data generation complete!"
echo ""
echo "📊 Output structure:"
echo "   ${OUTPUT_DIR}/fhir/          - FHIR JSON bundles (one per patient)"
echo "   ${OUTPUT_DIR}/fhir/*.json    - Patient records with clinical notes"
echo ""

# Step 4: Count generated files
PATIENT_COUNT=$(find "${OUTPUT_DIR}/fhir" -name "*.json" -type f | wc -l | tr -d ' ')
echo "📈 Generated ${PATIENT_COUNT} patient files"

# Step 5: Show sample clinical note
echo ""
echo "📝 Sample clinical note extraction:"
SAMPLE_FILE=$(find "${OUTPUT_DIR}/fhir" -name "*.json" -type f | head -1)
if [ -n "${SAMPLE_FILE}" ]; then
    echo "   From: $(basename ${SAMPLE_FILE})"
    echo ""
    # Extract first DocumentReference content (clinical note)
    python3 -c "
import json
import sys
with open('${SAMPLE_FILE}') as f:
    data = json.load(f)
    for entry in data.get('entry', []):
        resource = entry.get('resource', {})
        if resource.get('resourceType') == 'DocumentReference':
            content = resource.get('content', [{}])[0]
            attachment = content.get('attachment', {})
            if 'data' in attachment:
                import base64
                note = base64.b64decode(attachment['data']).decode('utf-8')
                print('   ' + note[:200] + '...')
                break
" 2>/dev/null || echo "   (Install Python to preview notes)"
fi

echo ""
echo "🎉 Next steps:"
echo "   1. Load FHIR data into PostgreSQL"
echo "   2. Extract features with BioBERT"
echo "   3. Retrain XGBoost model"
echo ""
echo "💡 To generate more patients: ./generate_synthea_data.sh 10000"
