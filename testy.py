import mysql.connector
import pandas as pd
import pytest

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
    cursor.execute ('''
        CREATE TABLE IF NOT EXISTS test_crud (
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
    cursor.execute("DROP TABLE IF EXISTS test_crud")
    connection.commit()
    cursor.close()
    connection.close()

def test_pridat_ukol(db_setup):
    connection, cursor = db_setup

    # Přidání úkolu
    nazev = "Testovací úkol"
    popis = "Toto je testovací popis."
    stav = "Nezahájeno"
    datum_v = "2024-01-01"

    dtb = "INSERT INTO test_crud (NAZEV, POPIS, STAV, DATUM_V) VALUES (%s, %s, %s, %s)"
    hodn = (nazev, popis, stav, datum_v)
    cursor.execute(dtb, hodn)
    connection.commit()

    # Ověření, že byl úkol přidán
    cursor.execute("SELECT * FROM test_crud WHERE NAZEV = %s", (nazev,))
    result = cursor.fetchone()
    assert result is not None
    assert result[1] == nazev
    assert result[2] == popis
    assert result[3] == stav
    assert str(result[4]) == datum_v

def test_aktualizovat_ukol(db_setup):
    connection, cursor = db_setup

    # Přidání úkolu pro aktualizaci
    nazev = "Úkol k aktualizaci"
    popis = "Popis před aktualizací."
    stav = "Nezahájeno"
    datum_v = "2024-01-01"

    dtb = "INSERT INTO test_crud (NAZEV, POPIS, STAV, DATUM_V) VALUES (%s, %s, %s, %s)"
    hodn = (nazev, popis, stav, datum_v)
    cursor.execute(dtb, hodn)
    connection.commit()

    # Aktualizace stavu úkolu
    cursor.execute("SELECT ID FROM test_crud WHERE NAZEV = %s", (nazev,))
    id_ukolu = cursor.fetchone()[0]

    novy_stav = "Probíhá"
    dtb_update = "UPDATE test_crud SET STAV = %s WHERE ID = %s"
    cursor.execute(dtb_update, (novy_stav, id_ukolu))
    connection.commit()

    # Ověření aktualizace
    cursor.execute("SELECT STAV FROM test_crud WHERE ID = %s", (id_ukolu,))
    updated_stav = cursor.fetchone()[0]
    assert updated_stav == novy_stav

def test_odstranit_ukol(db_setup):
    connection, cursor = db_setup

    # Přidání úkolu pro odstranění
    nazev = "Úkol k odstranění"
    popis = "Popis úkolu k odstranění."
    stav = "Nezahájeno"
    datum_v = "2024-01-01"

    dtb = "INSERT INTO test_crud (NAZEV, POPIS, STAV, DATUM_V) VALUES (%s, %s, %s, %s)"
    hodn = (nazev, popis, stav, datum_v)
    cursor.execute(dtb, hodn)
    connection.commit()

    # Získání ID úkolu
    cursor.execute("SELECT ID FROM test_crud WHERE NAZEV = %s", (nazev,))
    id_ukolu = cursor.fetchone()[0]

    # Odstranění úkolu
    sql_delete = "DELETE FROM test_crud WHERE ID = %s"
    cursor.execute(sql_delete, (id_ukolu,))
    connection.commit()

    # Ověření odstranění
    cursor.execute("SELECT * FROM test_crud WHERE ID = %s", (id_ukolu,))
    result = cursor.fetchone()
    assert result is None

def test_vlozit_neplatny_ukol(db_setup):
    connection, cursor = db_setup

    # Pokus o vložení úkolu s prázdným názvem
    nazev = ""
    popis = "Popis s prázdným názvem."
    stav = "Nezahájeno"
    datum_v = "2024-01-01"
   
    dtb = "INSERT INTO test_crud (NAZEV, POPIS, STAV, DATUM_V) VALUES (%s, %s, %s, %s)"
    hodn = (nazev, popis, stav, datum_v)
    with pytest.raises(mysql.connector.Error):
        cursor.execute(dtb, hodn)
    connection.commit()

def test_aktualizovat_neexistujici_ukol(db_setup):
    connection, cursor = db_setup

    # Pokus o aktualizaci neexistujícího úkolu
    id_ukolu = 9999  # Předpokládané neexistující ID
    novy_stav = "Probíhá"

    sql_update = "UPDATE test_crud SET STAV = %s WHERE ID = %s"
    cursor.execute(sql_update, (novy_stav, id_ukolu))
    connection.commit()

    # Ověření, že nebyl aktualizován žádný řádek
    assert cursor.rowcount == 0

def test_odstranit_neexistujici_ukol(db_setup):
    connection, cursor = db_setup

    # Pokus o odstranění neexistujícího úkolu
    id_ukolu = 9999  # Předpokládané neexistující ID

    sql_delete = "DELETE FROM test_crud WHERE ID = %s"
    cursor.execute(sql_delete, (id_ukolu,))
    connection.commit()

    # Ověření, že nebyl odstraněn žádný řádek
    assert cursor.rowcount == 0

if __name__ == "__main__":
  print("Spouštím testy...")
  pytest.main(["-v", "testy.py"])