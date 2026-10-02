#part of the game where asking about player location and the player distinction
#also the ticket prices
#the code not ready, it works as it is.

from geopy.distance import geodesic
import mysql.connector



datastorage = mysql.connector.connect(
    host='127.0.0.1',
    port= 3306,
    database= 'flight_game',
    user= 'root',
    password= '1234',
    autocommit= True
)

def check_name(country):            #checking the input (country name) is correct
    chk = f"select iso_country from country where name = '{country}'"
    cursor = datastorage.cursor()
    cursor.execute(chk)
    result = cursor.fetchall()
    cursor.close()
    if result:
        return True
    else:
        return False

def ticket_price(x,y):     #price checking the function not connected yet. (update 27.9.2026)
    dis = geodesic(x,y).km
    price = dis * 0.18
    return price

def rand_choice(starts): #random choise to next country.
    next_location = (f"select country.name from country join airport on  country.iso_country = airport.iso_country "
                     f"where airport.ident != %s order by rand() limit 1;")
    crosri = datastorage.cursor()
    crosri.execute(next_location, (starts,))
    values = crosri.fetchone()
    crosri.close()
    return values[0]

def airport_list(place):
    sql = (f"select airport.name, ident from airport join country on airport.iso_country = country.iso_country where "
           f"airport.type = 'large_airport' and country.name = '{place}' order by airport.iso_country;")
    crosri = datastorage.cursor()
    crosri.execute(sql)
    values = crosri.fetchall()
    places = []
    codes = []
    for i  in range(len(values)):
        places.append(values[i][0])

    for j in range(len(values)):
        codes.append(values[j][1])

    flights = dict(zip(codes, places))
    return flights

def airport_locations(airport_code): #pulling out locations
    gps_airport = f"select latitude_deg, longitude_deg from airport where ident = %s"
    crosri = datastorage.cursor()
    crosri.execute(gps_airport, (airport_code,))
    values = crosri.fetchall()
    crosri.close()
    return values


while True:
    first = input("where are you?  ").lower()
    final = input("where you want to go?  ").lower()

    if check_name(first) and  check_name(final):
        fcodes = airport_list(first)

        if len(fcodes) > 1: # creates dictionary of airport name and airport code, this for player location

            for code, airport in fcodes.items():
                print(f"{code}: {airport}")
            airport_choise1 = input("what airport are you in(entre airport code)?  ").upper()
            print(f"your airport is {fcodes[airport_choise1]}")
        else:
            airport_choise1, airport_name = next(iter(fcodes.items()))
            print(f"your airport is {airport_name}")

        codes = airport_list(final)


        if len(codes) > 1: #dictionary for distinction country
            for code, airport in codes.items():
                print(f"{code}: {airport}")
            airport_choise2 = input("\nwhat airport are you to go(entre airport code)?  ").upper()
            print(f"you're going to {codes[airport_choise2]}")
        else:
            airport_choise2, airport_name = next(iter(codes.items()))
            print(f"you're going to {airport_name}")
        break

    else:
        print("Please enter a valid name")
loc1 = airport_locations(airport_choise1)
loc2 = airport_locations(airport_choise2)

print(f"{ticket_price(loc1,loc2):.2f}€")

next_location = rand_choice(airport_choise2)
print(f"next destination: {next_location}")