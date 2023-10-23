# SCADA-Server

Backend for Impact Allies' SCADA software.

The frontend for the SCADA software can be found [here](https://github.com/create-scada/scada-client).

Sample output can be found [here](https://github.com/create-scada/scada-data). 

# Development server

Navigate to the scada-server directory in CMD and type `dotnet run` to run the backend.


NOTE: This software uses [postgreSQL](https://www.postgresql.org/download/) and [Npgsql](https://www.npgsql.org/doc/installation.html). Ensure that the postgreSQL environment variables in Program.cs are set properly before use.
