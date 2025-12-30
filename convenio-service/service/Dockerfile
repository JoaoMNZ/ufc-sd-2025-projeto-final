
FROM maven:3.8-openjdk-17 AS build
WORKDIR /app

# Copiar pom.xml e baixar dependências
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copiar código fonte
COPY src ./src

# Compilar e criar Fat JAR
RUN mvn clean package -DskipTests

# Listar arquivos gerados (debug)
RUN echo "=== Arquivos JAR gerados ===" && ls -lh /app/target/*.jar

# Stage 2: Runtime
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Copiar o JAR final (não o original)
COPY --from=build /app/target/convenio-service.jar app.jar

EXPOSE 5003

CMD ["java", "-jar", "app.jar"]