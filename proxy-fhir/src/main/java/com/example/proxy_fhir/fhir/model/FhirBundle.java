package com.example.proxy_fhir.fhir.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.Map;

@Entity
@Table(name = "fhir_bundles")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FhirBundle {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "bundle_type", nullable = false)
    private String bundleType;

    @Column(name = "patient_id", nullable = false)
    private String patientId;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "bundle_data", nullable = false, columnDefinition = "jsonb")
    private Map<String, Object> bundleData;

    @Column(name = "total_resources")
    private Integer totalResources;

    @Column(name = "sync_date", nullable = false)
    private LocalDateTime syncDate;

    @Column(name = "query_params")
    private String queryParams;

    @PrePersist
    protected void onCreate() {
        syncDate = LocalDateTime.now();
    }
}