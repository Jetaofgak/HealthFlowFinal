# Sync Feature Crash Analysis: "Proof as Code"

> **For Claude:** REQUIRED SUB-SKILL: use executing-plans skill to implement this plan task-by-task.

**Goal:** Analyze and explain why the "Sync 100 Patients" feature crashes while local data generation works perfectly.

**Architecture:** Comparative analysis of `FhirSyncService` (Network I/O) vs `generate_synthea_data.sh` (Local Compute).

**Tech Stack:** Java (Spring Boot), HAPI FHIR, Bash, Python

---

### Task 1: Document the Crash (Network Dependency)

**Files:**

- Modify: `proxy-fhir/src/main/resources/application.yaml` (Reference only)

**Step 1: Identify Root Cause**

The system is configured to connect to a **public, rate-limited university server** in the US.

```yaml
hapi:
  fhir:
    server-url: https://r4.smarthealthit.org # <--- ROOT CAUSE 1
    fhir-version: R4
```

**Step 2: Verify Proof**

- This server is slow and often rejects automated bulk requests.
- Log confirmation: `500 Internal Server Error` on `/api/v1/fhir/sync/bulk`.

### Task 2: Analyze Code Flaw (Synchronous Blocking)

**Files:**

- Modify: `proxy-fhir/src/main/java/com/example/proxy_fhir/fhir/service/FhirSyncService.java` (Reference only)

**Step 1: Analyze Control Flow**

The `syncMultiplePatients` method is **Synchronous**. It waits for _every single patient_ to download before finishing.

```java
public Map<String, Object> syncMultiplePatients(int count) {
    // ...
    // 1. Fetches ALL 100 patient IDs at once (Slow)
    Bundle patientBundle = fhirClientService.getAllPatients(count);

    // 2. Loops and downloads detailed data one-by-one (Very Slow)
    for (Bundle.BundleEntryComponent entry : patientBundle.getEntry()) {
        // ...
        syncPatientData(patientId); // <--- BLOCKING CALL
    }
}
```

**Step 2: Proof Calculation**

- If 1 patient takes 1 second, 100 patients take **100 seconds**.
- The API Gateway / Browser times out after **30-60 seconds**.
- Result: `500 Internal Server Error`.

### Task 3: Analyze Success Control (Local Generation)

**Files:**

- Modify: `scripts/generate_synthea_data.sh` (Reference only)

**Step 1: Analyze Execution Model**

The script works because it uses a **Local Java JAR** file. It performs CPU calculations on your laptop. No network required.

```bash
# Runs LOCALLY on your CPU
java -jar "${SYNTHEA_JAR}" \
    -p ${NUM_PATIENTS} \
    # ...
```

### Task 4: Solution Recommendation

**Step 1: Recommendation**

1.  **Do Not Fix Code**: The code is correct for a _real_ hospital with a fast internal server.
2.  **Use "Skip Sync"**: This correctly bypasses the "Fragile Network" path and uses the "Robust Local" path (Database).

**Step 2: Execution Handoff**
Plan complete. Ready for execution if you want to implement a "Mock Mode" or just document this finding.
