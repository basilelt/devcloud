# Use the official MySQL image as the base image
FROM mysql:latest

# Set the MySQL root password
ENV MYSQL_ROOT_PASSWORD=RootSQLG7

# Create a new user 'sql' with password 'sqlpassword'
ENV MYSQL_USER=sql
ENV MYSQL_PASSWORD=MYSQLG7

# Create a new database 'trafic'
ENV MYSQL_DATABASE=trafic

# Copy the database dump file to the container
COPY trafic.sql /docker-entrypoint-initdb.d/

# Run the MySQL server
CMD ["mysqld"]