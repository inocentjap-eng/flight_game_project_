import random
import mysql.connector
from geopy.distance import geodesic

ALKURAHA = 1000       # starting money (euros)
HINTA_KM = 0.18       # euros per kilometre
MIN_HINTA = 40        # minimum flight price (euros)
BONUS = 500           # level bonus = BONUS * level
KYNNYS_KM = 1000      # new target is at least KYNNYS_KM * level km away

yhteys = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    database="flight_game",
    user="root",
    password="1234",
    autocommit=True,
    use_pure=True
)

# Load the airport table once. The query deliberately has no coordinate filter.
kursori = yhteys.cursor()
tulos = kursori.fetchall()

# Keep only rows with both coordinates. Each airport is a tuple:
# (ident, name, latitude, longitude)
kentat = []
for rivi in tulos:
    if rivi[2] != None and rivi[3] != None:
        kentat.append((rivi[0], rivi[1], float(rivi[2]), float(rivi[3])))


def etsi_lahin_suunnassa(kentat, nykyinen, suunta):
    # Find the nearest airport north, south, east, or west of nykyinen.
    # Returns the airport and its distance in km. Distance -1 = no airport that way.
    lahimmat = []

    for kentta in kentat:
        if kentta[0] != nykyinen[0]:
            if suunta == "N" and kentta[2] > nykyinen[2]:
                lahimmat.append(kentta)
            elif suunta == "S" and kentta[2] < nykyinen[2]:
                lahimmat.append(kentta)
            elif suunta == "E" and kentta[3] > nykyinen[3]:
                lahimmat.append(kentta)
            elif suunta == "W" and kentta[3] < nykyinen[3]:
                lahimmat.append(kentta)

    lahin = nykyinen
    lahin_km = -1
    nykyinen_sijainti = (nykyinen[2], nykyinen[3])
    for kentta in lahimmat:
        kentan_sijainti = (kentta[2], kentta[3])
        km = geodesic(nykyinen_sijainti, kentan_sijainti).kilometers
        if lahin_km < 0 or km < lahin_km:
            lahin = kentta
            lahin_km = km
    return lahin, lahin_km


def valitse_tavoite(kentat, nykyinen, minimietaisyys):
    # Choose a different airport at least minimietaisyys kilometres away.
    mahdolliset = []
    nykyinen_sijainti = (nykyinen[2], nykyinen[3])

    for kentta in kentat:
        if kentta[0] != nykyinen[0]:
            kentan_sijainti = (kentta[2], kentta[3])
            matka = geodesic(nykyinen_sijainti, kentan_sijainti).kilometers
            if matka >= minimietaisyys:
                mahdolliset.append(kentta)

    # If no airport is far enough away, choose any different airport.
    if len(mahdolliset) == 0:
        for kentta in kentat:
            if kentta[0] != nykyinen[0]:
                mahdolliset.append(kentta)

    return mahdolliset[random.randint(0, len(mahdolliset) - 1)]


if len(kentat) < 2:
    print("The database needs at least two airports with coordinates.")
else:
    nykyinen = kentat[random.randint(0, len(kentat) - 1)]
    tavoite = valitse_tavoite(kentat, nykyinen, 0)
    rahat = ALKURAHA
    kokonaismatka = 0
    taso = 1
    pisteet = 0
    peli_kaynnissa = True

    print("Welcome to Flight Game!")

    while peli_kaynnissa and rahat > 0:
        print(f"\nCurrent airport: {nykyinen[1]} ({nykyinen[0]})")
        print(f"Target airport: {tavoite[1]} ({tavoite[0]})")
        print(f"Money: €{rahat}")
        print(f"Total distance: {kokonaismatka:.0f} km")
        print(f"Level: {taso}   Score: {pisteet}")

        suunta = input("Choose N, S, E, W, or Q to quit: ").strip().upper()

        if suunta == "Q":
            peli_kaynnissa = False
        elif suunta != "N" and suunta != "S" and suunta != "E" and suunta != "W":
            print("Invalid choice. Enter N, S, E, W, or Q.")
        else:
            kohde, matka = etsi_lahin_suunnassa(kentat, nykyinen, suunta)

            if matka < 0:
                print("There is no airport in that direction.")
            else:
                hinta = int(matka * HINTA_KM + 0.5)
                if hinta < MIN_HINTA:
                    hinta = MIN_HINTA

                print(f"Destination: {kohde[1]} ({kohde[0]})")
                print(f"Distance: {matka:.0f} km")
                print(f"Flight price: €{hinta}")

                if hinta > rahat:
                    print("You do not have enough money for this flight.")
                else:
                    vastaus = input("Fly there? (Y/N): ").strip().upper()
                    if vastaus == "Y":
                        nykyinen = kohde
                        rahat = rahat - hinta
                        kokonaismatka = kokonaismatka + matka
                        pisteet = pisteet + int(matka + 0.5)
                        print(f"You landed at {nykyinen[1]}.")

                        if nykyinen[0] == tavoite[0]:
                            bonus = taso * BONUS
                            pisteet = pisteet + bonus
                            print(f"Target reached! Level bonus: {bonus} points.")
                            taso = taso + 1
                            tavoite = valitse_tavoite(kentat, nykyinen, KYNNYS_KM * taso)
                            print(f"New target: {tavoite[1]} ({tavoite[0]})")
                    else:
                        print("Flight cancelled. Nothing changed.")

    print("\nGame over.")
    print(f"Total distance flown: {kokonaismatka:.0f} km")
    print(f"Level reached: {taso}")
    print(f"Final score: {pisteet}")