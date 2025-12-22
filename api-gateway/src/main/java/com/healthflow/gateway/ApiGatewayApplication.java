package com.healthflow.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@SpringBootApplication
@RestController
public class ApiGatewayApplication {

	public static void main(String[] args) {
		SpringApplication.run(ApiGatewayApplication.class, args);
	}

	@GetMapping("/")
	public Map<String, Object> home() {
		Map<String, Object> response = new HashMap<>();
		response.put("service", "HealthFlow API Gateway");
		response.put("version", "1.0.0");
		response.put("status", "UP");

		Map<String, String> routes = new HashMap<>();
		routes.put("ProxyFHIR", "/api/v1/fhir/*");
		routes.put("DeID", "/api/v1/deid/*");
		routes.put("Featurizer", "/api/v1/features/*");
		routes.put("ML-Predictor", "/api/v1/predictions/*");

		response.put("available_routes", routes);

		return response;
	}

	@CrossOrigin(origins = "*")
	@GetMapping("/health")
	public Map<String, String> health() {
		Map<String, String> response = new HashMap<>();
		response.put("status", "UP");
		response.put("service", "API Gateway");
		return response;
	}
}
