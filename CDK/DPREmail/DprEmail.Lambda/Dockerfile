FROM mcr.microsoft.com/dotnet/core/sdk:2.1 AS build-env
WORKDIR /dpr.email

# Install dependencies
RUN apt-get update -y
RUN apt-get install zip -y
RUN dotnet tool install -g Amazon.Lambda.Tools
ENV PATH="/root/.dotnet/tools:${PATH}"
RUN echo $PATH

COPY . ./

# Copy everything else and build
RUN dotnet restore
RUN dotnet lambda package

