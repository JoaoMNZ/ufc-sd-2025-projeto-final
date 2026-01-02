# Usamos uma imagem mais moderna do Maven para evitar erros de 403
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /app

# Copia todo o projeto
COPY . .

# Compila direto (removemos o go-offline que estava falhando)
RUN mvn clean package -DskipTests

# --- Parte 2: Imagem Final Leve ---
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Pega o JAR que foi gerado no passo anterior
COPY --from=build /app/target/convenio-service.jar app.jar

EXPOSE 5003

CMD ["java", "-jar", "app.jar"]