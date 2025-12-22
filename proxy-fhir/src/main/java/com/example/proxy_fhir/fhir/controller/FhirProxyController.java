package com.example.proxy_fhir.fhir.controller;

import com.example.proxy_fhir.fhir.client.FhirClientService;
import com.example.proxy_fhir.fhir.service.FhirSyncService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.hl7.fhir.r4.model.Bundle;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/fhir")
@RequiredArgsConstructor
@Slf4j
public class FhirProxyController {

    private final FhirClientService fhirClientService;
    private final FhirSyncService fhirSyncService;

    /**
     * Synchronise plusieurs patients en masse
     */
    @PostMapping("/sync/bulk")
    public ResponseEntity<Map<String, Object>> syncBulkPatients(
            @RequestParam(defaultValue = "100") int count) {
        log.info("POST /fhir/sync/bulk with count={}", count);
        Map<String, Object> result = fhirSyncService.syncMultiplePatients(count);
        return ResponseEntity.ok(result);
    }

    /**
     * Récupère un patient par ID
     */
    @GetMapping("/patients/{patientId}")
    public ResponseEntity<Map<String, Object>> getPatient(@PathVariable String patientId) {
        log.info("GET /fhir/patients/{}", patientId);
        Map<String, Object> patient = fhirClientService.getPatientById(patientId);
        return ResponseEntity.ok(patient);
    }

    /**
     * Recherche des patients
     */
    @GetMapping("/patients/search")
    public ResponseEntity<Map<String, Object>> searchPatients(
            @RequestParam Map<String, String> searchParams) {
        log.info("GET /fhir/patients/search with params: {}", searchParams);
        Bundle bundle = fhirClientService.searchPatients(searchParams);
        return ResponseEntity.ok(fhirClientService.bundleToMap(bundle));
    }

    /**
     * Récupère les observations d'un patient
     */
    @GetMapping("/patients/{patientId}/observations")
    public ResponseEntity<Map<String, Object>> getPatientObservations(
            @PathVariable String patientId) {
        log.info("GET /fhir/patients/{}/observations", patientId);
        Bundle bundle = fhirClientService.getPatientObservations(patientId);
        return ResponseEntity.ok(fhirClientService.bundleToMap(bundle));
    }

    /**
     * Synchronise les données d'un patient
     */
    @PostMapping("/sync/patient/{patientId}")
    public ResponseEntity<Map<String, Object>> syncPatient(@PathVariable String patientId) {
        log.info("POST /fhir/sync/patient/{}", patientId);
        int resourceCount = fhirSyncService.syncPatientData(patientId);

        return ResponseEntity.ok(Map.of(
                "status", "success",
                "patientId", patientId,
                "resourcesSynced", resourceCount));
    }

    /**
     * Récupère les statistiques de synchronisation
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Long>> getStats() {
        log.info("GET /fhir/stats");
        return ResponseEntity.ok(fhirSyncService.getSyncStatistics());
    }

    /**
     * Health check
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of(
                "status", "UP",
                "service", "ProxyFHIR"));
    }

    /**
     * Compte le nombre de patients
     */
    @GetMapping("/count")
    public ResponseEntity<Map<String, Long>> getCount() {
        log.info("GET /fhir/count");
        long count = fhirSyncService.getPatientCount();
        return ResponseEntity.ok(Map.of("count", count));
    }

    @PostMapping("/generate")
    public ResponseEntity<Map<String, Object>> generatePatients(@RequestParam(defaultValue = "1") int count) {
        log.info("POST /fhir/generate count={}", count);
        Map<String, Object> result = fhirSyncService.generatePatients(count);
        return ResponseEntity.ok(result);
    }
}