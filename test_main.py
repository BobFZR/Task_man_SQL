import mysql.connector
import pandas as pd
import pytest
from main import pridat_ukol, aktualizovat_ukol, odstranit_ukol


@pytest.fixture(scope="function")
def db_setup():
    """
    Fixture pro připojení k databbázi a nastavení testovacího prostředí.
    """
    # Připojení k databázi
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Bob/123456",
        )
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS test_db")
    connection.database = "test_db"
    cursor.execute("USE test_db")
    connection.commit()
    cursor.execute ('''
        CREATE TABLE IF NOT EXISTS ukoly (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            NAZEV VARCHAR(255) NOT NULL CHECK (LENGTH(NAZEV) > 0),
            POPIS TEXT NOT NULL CHECK (LENGTH(POPIS) > 0),
            STAV VARCHAR(20) NOT NULL,
            DATUM_V DATE NOT NULL
        )
    ''')
    connection.commit()

    yield connection, cursor

    # Uzavření a odstranění databáze po testech
    cursor.execute("DROP TABLE IF EXISTS ukoly")
    connection.commit()
    cursor.close()
    connection.close()

def test_pridat_ukol_positiv(db_setup):
    connection, cursor = db_setup

    # Přidání úkolu
    
    nazev = "Testovací úkol"
    popis = "Toto je testovací popis."
    stav = "Nezahájeno"
    datum_v = "2024-01-01"
    pridat_ukol(cursor, nazev, popis, stav, datum_v)
    connection.commit()

    # Ověření, že byl úkol přidán
    cursor.execute("SELECT * FROM ukoly WHERE NAZEV = %s", (nazev,))
    result = cursor.fetchone()
    assert result is not None
    assert result[1] == nazev
    assert result[2] == popis
    assert result[3] == stav
    assert str(result[4]) == datum_v

def test_aktualizovat_ukol_positiv(db_setup):
    connection, cursor = db_setup

    # Přidání úkolu pro aktualizaci
    nazev = "Úkol k aktualizaci"
    popis = "Popis před aktualizací."
    stav = "Nezahájeno"
    datum_v = "2024-01-01"
    
    dtb = "INSERT INTO ukoly (NAZEV, POPIS, STAV, DATUM_V) VALUES (%s, %s, %s, %s)"
    hodn = (nazev, popis, stav, datum_v)
    cursor.execute(dtb, hodn)
    connection.commit()

    # Aktualizace stavu úkolu

    cursor.execute("SELECT ID FROM ukoly WHERE NAZEV = %s", (nazev,))
    id_ukolu = cursor.fetchone()[0]
    connection.commit()
    novy_stav = "Probíhá"
    aktualizovat_ukol(cursor, id_ukolu, novy_stav)
    connection.commit()

    # Ověření aktualizace
    cursor.execute("SELECT STAV FROM ukoly WHERE ID = %s", (id_ukolu,))
    updated_stav = cursor.fetchone()[0]
    assert updated_stav == novy_stav

def test_odstranit_ukol_positiv(db_setup):
    connection, cursor = db_setup

    # Přidání úkolu pro odstranění
    nazev = "Úkol k odstranění"
    popis = "Popis úkolu k odstranění."
    stav = "Nezahájeno"
    datum_v = "2024-01-01"

    dtb = "INSERT INTO ukoly (NAZEV, POPIS, STAV, DATUM_V) VALUES (%s, %s, %s, %s)"
    hodn = (nazev, popis, stav, datum_v)
    cursor.execute(dtb, hodn)
    connection.commit()

    # Získání ID úkolu
    cursor.execute("SELECT ID FROM ukoly WHERE NAZEV = %s", (nazev,))
    id_ukolu = cursor.fetchone()[0]

    # Odstranění úkolu
    odstranit_ukol(cursor, id_ukolu)
    connection.commit()

    # Ověření odstranění
    cursor.execute("SELECT * FROM ukoly WHERE ID = %s", (id_ukolu,))
    result = cursor.fetchone()
    assert result is None

def test_pridat_ukol_negativ(db_setup):
    connection, cursor = db_setup

    # Pokus o vložení úkolu s prázdným názvem
    nazev = ""
    popis = "Popis s prázdným názvem."
    stav = "Nezahájeno"
    datum_v = "2024-01-01"

    result = pridat_ukol(cursor, nazev, popis, stav, datum_v)
    connection.commit()

    # Ověření, že úkol nebyl přidán
    cursor.execute("SELECT * FROM ukoly WHERE NAZEV = %s", (nazev,))
    result = cursor.fetchone()
    assert result is None
    

def test_aktualizovat_ukol_negativ(db_setup):
    connection, cursor = db_setup

    # Pokus o aktualizaci neexistujícího úkolu
    id_ukolu = 9999  # Předpokládané neexistující ID
    novy_stav = "Probíhá"
    aktualizovat_ukol(cursor, id_ukolu, novy_stav)
    connection.commit()

    # Ověření, že nebyl aktualizován žádný řádek
    assert cursor.rowcount == 0

def test_odstranit_ukol_negativ(db_setup):
    connection, cursor = db_setup

    # Pokus o odstranění neexistujícího úkolu
    id_ukolu = 9999  # Předpokládané neexistující ID

    odstranit_ukol(cursor, id_ukolu)
    connection.commit()

    # Ověření, že nebyl odstraněn žádný řádek
    assert cursor.rowcount == 0

