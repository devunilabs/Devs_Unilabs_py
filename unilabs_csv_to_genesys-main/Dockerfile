# Use the Microsoft SQL Server Docker image
FROM mcr.microsoft.com/azure-sql-edge

# Set the environment variables for SQL Server
ENV ACCEPT_EULA=Y
ENV SA_PASSWORD=Your_Password123

# Expose the SQL Server port
EXPOSE 1433

# Copy any additional SQL scripts or initialization files
# COPY init.sql /docker-entrypoint-initdb.d/