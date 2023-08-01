import pyodbc
import json


def createTables(connection, cursor):
    cursor.execute('''
                    CREATE TABLE Stations (
                        Id varchar(20) primary key,
                        Name varchar(60),
                        Latitude decimal(8,6),
                        Longitude decimal(8,6)
                    )
                   ''')
    
    connection.commit()

    cursor.execute('''
                    CREATE TABLE LineStations (
                        Id int primary key IDENTITY(1,1),
                        LineName varchar(60),
                        StationId varchar(20),
                        FOREIGN KEY (StationId) REFERENCES Stations(Id)
                    )
                   ''')
    
    connection.commit()


def insertData(connection, cursor):
    with open("train-network.json") as JsonFile:
        data = json.load(JsonFile)

    for station in data['stations']:
        cursor.execute('''
                    INSERT INTO Stations (Id, Name, Latitude, Longitude) 
                       VALUES(?, ?, ?, ?)
                   ''', (station['id'], station['name'], station['latitude'], station['longitude']))
        connection.commit()


    for line in data['lines']:
        for station in line['stations']:
            cursor.execute('''
                    INSERT INTO LineStations (LineName, StationId) 
                       VALUES(?, ?)
                   ''', (line['name'], station))
        connection.commit()


def printStationsByLine(cursor, line):
    cursor.execute('''
            SELECT s.Name
            FROM LineStations AS ls
            JOIN Stations AS s ON (ls.StationId = s.Id)
            WHERE ls.LineName = ?;
        ''', line)

    print()
    print(line + ' Line Stations:')
    print()

    for station, in cursor.fetchall():
        print(station)
    print()


def printLinesByStation(cursor, station):
    cursor.execute('''
            SELECT ls.LineName
            FROM Stations AS s
            JOIN LineStations AS ls ON (ls.StationId = s.Id)
            WHERE s.Name = ?;
        ''', station)

    print()
    print(station + ' Station Lines:')
    print()

    for line, in cursor.fetchall():
        print(line)
    print()


def display_options():
    print("Choose an option:")
    print("1. Get station name by line name")
    print("2. Get line name by station name")
    print("Type 'exit' to quit")


if __name__ == '__main__':
    server = 'localhost'
    database = 'UndergroundData'
    username = 'sa'
    password = 'Pass1234'
    driver = 'ODBC Driver 18 for SQL Server'

    connectionString = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes"

    try:
        connection= pyodbc.connect(connectionString)
        cursor = connection.cursor()

    except pyodbc.Error as e:
        print(e)
        exit()

    createTables(connection, cursor)
    insertData(connection, cursor)

    while True:
        print()
        print()

        display_options()
        option = input("Enter your choice: ").strip().lower()
        
        if option == '1':
            lineName = input("Enter line name: ").strip().lower()
            printStationsByLine(cursor, lineName)

        elif option == '2':
            stationName = input("Enter station name: ").strip().lower()
            printLinesByStation(cursor, stationName)

        elif option == 'exit':
            print("Exiting the application")
            quit()
        else:
            print("Invalid choice. Please try again.")
 