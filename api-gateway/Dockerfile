FROM eclipse-temurin:17-jre
WORKDIR /app

# Copy the JAR built locally on the host
COPY target/*.jar app.jar

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
