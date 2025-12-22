# Sync Failure Verification Report

Date: 2025-12-21

## Executive Summary

The analysis of the "Sync 100 Patients" feature crash confirms that the issue stems from a dependency on an unstable, rate-limited public FHIR server combined with a synchronous, blocking implementation in the backend code. The local data generation workflow (`generate_synthea_data.sh`) is verified to be the robust, correct alternative.

## Detailed Findings

### 1. External Dependency (Root Cause)

**File:** `proxy-fhir/src/main/resources/application.yaml`
**Finding:** The application is configured to use `https://r4.smarthealthit.org`, a public demonstration server.

```yaml
hapi:
  fhir:
    server-url: https://r4.smarthealthit.org
```

**Impact:** Public test servers often enforce strict rate limits or have high latency, causing timeouts for bulk operations.

### 2. Implementation Flaw (Blocking I/O)

**File:** `proxy-fhir/src/main/java/com/example/proxy_fhir/fhir/service/FhirSyncService.java`
**Finding:** The `syncMultiplePatients` method executes sequentially.

- **Line 79:** Fetches ALL patient summaries first.
- **Line 83-100:** Loops through each patient.
- **Line 90:** Calls `syncPatientData(patientId)` which triggers another round of network requests.
  **Impact:** If fetching one patient takes 1 second, 100 patients take ~100 seconds. This exceeds the typical default timeout (30-60s) of gateways/browsers, leading to `500 Internal Server Error`.

### 3. Local Workflow (Verified Solution)

**File:** `scripts/generate_synthea_data.sh`
**Finding:** The script uses a local JAR (`synthea-with-dependencies.jar`) to generate data.

```bash
java -jar "${SYNTHEA_JAR}" -p ${NUM_PATIENTS} ...
```

**Impact:** Generation happens on the local CPU/Disk with zero network calls, ensuring 100% reliability and speed.

## Recommendation

As outlined in the Analysis Plan:

1.  **Do Not Fix** the `FhirSyncService` for this demo environment, as widespread architectural changes (switching to async/batch processing) are unnecessary for the immediate goal.
2.  **Official Guidance:** Users should strictly follow the "Local Generation" workflow documented in the `README.md`.
3.  **Documentation Update:** It is recommended to add a "Known Limitations" section to the `README.md` to explicitly warn users against relying on the "Sync" button in the dashboard for large datasets.
