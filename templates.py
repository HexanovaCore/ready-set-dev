"""
Auto Dev Environment Setup - Enterprise Templates Manager
Author: HexanovaCore
Version: 1.2.0
Description: Ultimate production-ready templates for 8+ languages.
             Fully bulletproofed against Python string template interpolation errors ($$).
"""

from string import Template
from typing import Dict


# ==========================================
# 1. DOCKERFILE TEMPLATES (MULTI-STAGE & SECURE)
# ==========================================
DOCKER_TEMPLATES: Dict[str, Template] = {
    "python": Template('''FROM python:${version}-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:${version}-slim AS runner
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$$PATH
EXPOSE ${port}
CMD ["python", "main.py"]
'''),

    "node": Template('''FROM node:${version}-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

FROM node:${version}-alpine AS runner
WORKDIR /app
COPY --from=builder /app ./
EXPOSE ${port}
CMD ["npm", "start"]
'''),

    "typescript": Template('''FROM node:${version}-alpine AS builder
WORKDIR /app
COPY package*.json tsconfig.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:${version}-alpine AS runner
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY --from=builder /app/dist ./dist
EXPOSE ${port}
CMD ["node", "dist/index.js"]
'''),

    "go": Template('''FROM golang:${version}-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download || true
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

FROM alpine:latest AS runner
WORKDIR /app
COPY --from=builder /app/main .
EXPOSE ${port}
CMD ["./main"]
'''),

    "rust": Template('''FROM rust:${version}-slim AS builder
WORKDIR /app
COPY . .
RUN cargo build --release

FROM debian:bookworm-slim AS runner
WORKDIR /app
COPY --from=builder /app/target/release/${project_name} .
EXPOSE ${port}
CMD ["./${project_name}"]
'''),

    "java": Template('''FROM maven:3.9-eclipse-temurin-${version}-alpine AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:${version}-jre-alpine AS runner
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE ${port}
CMD ["java", "-jar", "app.jar"]
'''),

    "dotnet": Template('''FROM mcr.microsoft.com/dotnet/sdk:${version} AS builder
WORKDIR /app
COPY *.csproj ./
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o out

FROM mcr.microsoft.com/dotnet/aspnet:${version} AS runner
WORKDIR /app
COPY --from=builder /app/out .
EXPOSE ${port}
ENV ASPNETCORE_URLS=http://+:${port}
CMD ["dotnet", "${project_name}.dll"]
'''),

    "cpp": Template('''FROM ubuntu:24.04 AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential cmake ninja-build git ca-certificates \\
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
RUN cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
RUN cmake --build build

FROM ubuntu:24.04 AS runner
WORKDIR /app
COPY --from=builder /app/build/${project_name} .
EXPOSE ${port}
CMD ["./${project_name}"]
''')
}


# ==========================================
# 2. BULLETPROOF VS CODE SETTINGS TEMPLATES
# ==========================================
# DİKKAT: Tüm ${workspaceFolder} alanları Python Template crash koruması için $${workspaceFolder} yapılmıştır!
VSCODE_SETTINGS: Dict[str, Template] = {
    "python": Template('''{
    "python.defaultInterpreterPath": "$${workspaceFolder}/venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}'''),

    "node": Template('''{
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.codeActionsOnSave": { "source.fixAll.eslint": "explicit" }
}'''),

    "typescript": Template('''{
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "typescript.tsdk": "node_modules/typescript/lib",
    "editor.codeActionsOnSave": { "source.fixAll.eslint": "explicit" }
}'''),

    "go": Template('''{
    "editor.formatOnSave": true,
    "[go]": {
        "editor.defaultFormatter": "golang.go",
        "editor.codeActionsOnSave": { "source.organizeImports": "explicit" }
    }
}'''),

    "rust": Template('''{
    "rust-analyzer.linkedProjects": ["Cargo.toml"],
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "rust-lang.rust-analyzer"
}'''),

    "java": Template('''{
    "java.configuration.updateBuildConfiguration": "automatic",
    "editor.formatOnSave": true
}'''),

    "dotnet": Template('''{
    "dotnet.server.useOmnisharp": false,
    "csharp.backgroundAnalysis.analyzerDiagnosticsScope": "fullSolution",
    "editor.formatOnSave": true
}'''),

    "cpp": Template('''{
    "editor.formatOnSave": true,
    "C_Cpp.formatting": "clang-format",
    "C_Cpp.default.configurationProvider": "ms-vscode.cmake-tools",
    "cmake.configureOnOpen": true,
    "cmake.buildDirectory": "$${workspaceFolder}/build"
}''')
}


# ==========================================
# 3. MANIFEST / MANIFESTO TEMPLATES
# ==========================================
MANIFEST_TEMPLATES: Dict[str, Template] = {
    "python": Template('''# Core Dependencies
requests==2.31.0
rich==13.7.0

# Dev Dependencies
pytest==8.0.0
black==24.1.1
'''),

    "node": Template('''{
  "name": "${project_name}",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": { 
    "start": "node index.js" 
  },
  "dependencies": {},
  "devDependencies": {}
}'''),

    "typescript": Template('''{
  "name": "${project_name}",
  "version": "1.0.0",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node-dev --respawn index.ts"
  },
  "dependencies": {},
  "devDependencies": {
    "typescript": "^5.3.3",
    "ts-node-dev": "^2.0.0",
    "@types/node": "^20.11.0"
  }
}'''),

    "go": Template('''module ${project_name}

go ${version}
'''),

    "rust": Template('''[package]
name = "${project_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "1.35", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
'''),

    "java": Template('''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.autodev</groupId>
    <artifactId>${project_name}</artifactId>
    <version>1.0-SNAPSHOT</version>
    <properties>
        <maven.compiler.source>${version}</maven.compiler.source>
        <maven.compiler.target>${version}</maven.compiler.target>
    </properties>
</project>
'''),

    "dotnet": Template('''<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net${version}</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
'''),

    "cpp": Template('''cmake_minimum_required(VERSION 3.22)
project(${project_name} VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD ${version})
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(${project_name} main.cpp)
''')
}


# ==========================================
# 4. PRIMARY SOURCE CODE TEMPLATES
# ==========================================
SOURCE_TEMPLATES: Dict[str, Template] = {
    "python": Template('print("🚀 ${project_name} projesi ayağa kalktı!")\n'),
    "node": Template('console.log("🚀 ${project_name} projesi ayağa kalktı!");\n'),
    "typescript": Template('console.log("🚀 ${project_name} TypeScript projesi ayağa kalktı!");\n'),
    "go": Template('''package main
import "fmt"

func main() {
    fmt.Println("🚀 ${project_name} projesi ayağa kalktı!")
}
'''),
    "rust": Template('''fn main() {
    println!("🚀 ${project_name} projesi ayağa kalktı!");
}
'''),
    "java": Template('''package com.autodev;

public class Main {
    public static void main(String[] args) {
        System.out.println("🚀 ${project_name} projesi ayağa kalktı!");
    }
}
'''),
    "dotnet": Template('Console.WriteLine("🚀 ${project_name} projesi ayağa kalktı!");\n'),
    "cpp": Template('''#include <iostream>

int main() {
    std::cout << "🚀 ${project_name} projesi C++${version} ile ayağa kalktı!" << std::endl;
    return 0;
}
''')
}


# ==========================================
# 5. TEMPLATE PUBLIC API MANAGER
# ==========================================
class TemplateManager:
    """Şablon motorunu dış dünyaya güvenli ve soyutlanmış olarak sunan API."""

    @staticmethod
    def get_dockerfile(language: str, project_name: str, version: str, port: int = 8080) -> str:
        """Dinamik olarak Multi-Stage Dockerfile render eder."""
        template = DOCKER_TEMPLATES.get(language.lower())
        if not template:
            raise ValueError(f"Docker template not found for: {language}")
        return template.substitute(project_name=project_name, version=version, port=port)

    @staticmethod
    def get_vscode_settings(language: str) -> str:
        """Kilitlenmeye karşı korumalı .vscode ayar şablonunu döner."""
        template = VSCODE_SETTINGS.get(language.lower())
        if not template:
            raise ValueError(f"VS Code template not found for: {language}")
        return template.substitute()

    @staticmethod
    def get_manifest(language: str, project_name: str, version: str) -> str:
        """Gerekli bağımlılık (manifest) dosyası içeriğini döner."""
        template = MANIFEST_TEMPLATES.get(language.lower())
        if not template:
            raise ValueError(f"Manifest template not found for: {language}")
        return template.substitute(project_name=project_name, version=version)

    @staticmethod
    def get_source_code(language: str, project_name: str, version: str) -> str:
        """Dil bazlı ilksel giriş kod şablonunu döner."""
        template = SOURCE_TEMPLATES.get(language.lower())
        if not template:
            raise ValueError(f"Source template not found for: {language}")
        return template.substitute(project_name=project_name, version=version)
