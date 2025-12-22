package com.example.proxy_fhir.fhir.service;

import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.parser.IParser;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.example.proxy_fhir.fhir.client.FhirClientService;
import com.example.proxy_fhir.fhir.model.FhirBundle;
import com.example.proxy_fhir.fhir.model.FhirResource;
import com.example.proxy_fhir.fhir.repository.FhirBundleRepository;
import com.example.proxy_fhir.fhir.repository.FhirResourceRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.hl7.fhir.r4.model.Bundle;
import org.hl7.fhir.r4.model.Resource;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class FhirSyncService {

    private final FhirClientService fhirClientService;
    private final FhirResourceRepository resourceRepository;
    private final FhirBundleRepository bundleRepository;
    private final FhirContext fhirContext;
    private final ObjectMapper objectMapper;

    /**
     * Synchronise toutes les données d'un patient
     */
    @Transactional
    public int syncPatientData(String patientId) {
        log.info("Starting sync for patient: {}", patientId);

        int resourceCount = 0;

        try {
            // Récupérer le Bundle complet du patient
            Bundle patientBundle = fhirClientService.getPatientEverything(patientId);

            // Sauvegarder le Bundle
            saveFhirBundle(patientBundle, "patient-everything", "patientId=" + patientId);

            // Extraire et sauvegarder chaque ressource
            for (Bundle.BundleEntryComponent entry : patientBundle.getEntry()) {
                Resource resource = entry.getResource();
                saveFhirResource(resource);
                resourceCount++;
            }

            log.info("Synced {} resources for patient: {}", resourceCount, patientId);

        } catch (Exception e) {
            log.error("Error syncing patient data: {}", e.getMessage(), e);
            throw new RuntimeException("Sync failed for patient: " + patientId, e);
        }

        return resourceCount;
    }
    /**
     * Synchronise plusieurs patients
     */
    @Transactional
    public Map<String, Object> syncMultiplePatients(int count) {
        log.info("Starting bulk sync for {} patients", count);
        List<String> syncedPatients = new ArrayList<>();
        List<String> failedPatients = new ArrayList<>();
        int totalResources = 0;

        try {
            // Récupérer tous les patients
            Bundle patientBundle = fhirClientService.getAllPatients(count);
            log.info("Found {} patients", patientBundle.getEntry().size());

            // Synchroniser chaque patient
            for (Bundle.BundleEntryComponent entry : patientBundle.getEntry()) {
                if (entry.getResource() instanceof org.hl7.fhir.r4.model.Patient) {
                    org.hl7.fhir.r4.model.Patient patient =
                            (org.hl7.fhir.r4.model.Patient) entry.getResource();
                    String patientId = patient.getIdElement().getIdPart();

                    try {
                        int resourceCount = syncPatientData(patientId);
                        syncedPatients.add(patientId);
                        totalResources += resourceCount;
                        log.info("Synced patient {}/{}: {} ({} resources)",
                                syncedPatients.size(), count, patientId, resourceCount);
                    } catch (Exception e) {
                        log.error("Failed to sync patient {}: {}", patientId, e.getMessage());
                        failedPatients.add(patientId);
                    }
                }
            }

            log.info("Bulk sync completed. Success: {}, Failed: {}, Total resources: {}",
                    syncedPatients.size(), failedPatients.size(), totalResources);

            return Map.of(
                    "status", "success",
                    "synced", syncedPatients.size(),
                    "failed", failedPatients.size(),
                    "totalResources", totalResources,
                    "syncedPatientIds", syncedPatients,
                    "failedPatientIds", failedPatients
            );

        } catch (Exception e) {
            log.error("Error in bulk sync: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to sync multiple patients", e);
        }
    }

    /**
     * Sauvegarde une ressource FHIR individuelle
     */
    @Transactional
    public void saveFhirResource(Resource resource) {
        try {
            String fhirId = resource.getIdElement().getIdPart();
            String resourceType = resource.getResourceType().name();

            // Vérifier si la ressource existe déjà
            FhirResource existingResource = resourceRepository
                    .findByFhirId(fhirId)
                    .orElse(null);

            // Convertir la ressource en JSON Map
            IParser jsonParser = fhirContext.newJsonParser();
            String jsonString = jsonParser.encodeResourceToString(resource);
            @SuppressWarnings("unchecked")
            Map<String, Object> resourceData = objectMapper.readValue(jsonString, Map.class);

            if (existingResource != null) {
                // Mise à jour
                existingResource.setResourceData(resourceData);
                existingResource.setLastUpdated(LocalDateTime.now());
                existingResource.setSyncDate(LocalDateTime.now());
                resourceRepository.save(existingResource);
                log.debug("Updated resource: {} - {}", resourceType, fhirId);
            } else {
                // Nouvelle ressource
                FhirResource newResource = FhirResource.builder()
                        .fhirId(fhirId)
                        .resourceType(resourceType)
                        .resourceData(resourceData)
                        .versionId(resource.getMeta().getVersionId())
                        .lastUpdated(resource.getMeta().getLastUpdated() != null
                                ? resource.getMeta().getLastUpdated().toInstant()
                                .atZone(ZoneId.systemDefault()).toLocalDateTime()
                                : LocalDateTime.now())
                        .build();

                resourceRepository.save(newResource);
                log.debug("Saved new resource: {} - {}", resourceType, fhirId);
            }

        } catch (Exception e) {
            log.error("Error saving FHIR resource: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to save FHIR resource", e);
        }
    }

    /**
     * Sauvegarde un Bundle FHIR complet
     */
    @Transactional
    public void saveFhirBundle(Bundle bundle, String bundleType, String queryParams) {
        try {
            IParser jsonParser = fhirContext.newJsonParser();
            String jsonString = jsonParser.encodeResourceToString(bundle);
            @SuppressWarnings("unchecked")
            Map<String, Object> bundleData = objectMapper.readValue(jsonString, Map.class);

            // Extract patient ID from queryParams (format: "patientId=xxx")
            String patientId = null;
            if (queryParams != null && queryParams.contains("patientId=")) {
                patientId = queryParams.substring(queryParams.indexOf("patientId=") + 10);
                if (patientId.contains("&")) {
                    patientId = patientId.substring(0, patientId.indexOf("&"));
                }
            }

            if (patientId == null) {
                log.error("Patient ID not found in queryParams: {}", queryParams);
                throw new IllegalArgumentException("Patient ID is required but was not found in queryParams");
            }

            FhirBundle fhirBundle = FhirBundle.builder()
                    .bundleType(bundleType)
                    .patientId(patientId)
                    .bundleData(bundleData)
                    .totalResources(bundle.getEntry().size())
                    .queryParams(queryParams)
                    .build();

            bundleRepository.save(fhirBundle);
            log.info("Saved FHIR Bundle: type={}, patientId={}, resources={}", bundleType, patientId, bundle.getEntry().size());

        } catch (Exception e) {
            log.error("Error saving FHIR bundle: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to save FHIR bundle", e);
        }
    }

    /**
     * Récupère les statistiques de synchronisation
     */
    public Map<String, Long> getSyncStatistics() {
        List<Object[]> stats = resourceRepository.countByResourceType();
        Map<String, Long> statistics = new java.util.HashMap<>();

        for (Object[] stat : stats) {
            statistics.put((String) stat[0], (Long) stat[1]);
        }

        return statistics;
    }

}