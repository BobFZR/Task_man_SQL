import mysql.connector
import pandas as pd
from datetime import date

def pripojeni_db():
  dataBase = None
  try:
    dataBase = mysql.connector.connect(
      host="localhost",
      user="root",
      password="Bob/123456"
    )
    print("Připojení k databázi proběhlo úspěšně.")
  except mysql.connector.Error as error:
    print(f"Připojení k databázi selhalo: {error}")
  
  return dataBase
  
def hlavni_menu():
  print()
  print("Správce úkolů - Hlavní menu")
  print("1. Přidat úkol")
  print("2. Zobrazit úkoly")
  print("3. Aktualizovat úkol")
  print("4. Odstranit úkol")
  print("5. Ukončit program")
  volba = input("Vyberte možnost(1-5): ")
  print()
  return volba

def vytvoreni_tabulky(cursor):
  cursor.execute('''
   CREATE TABLE IF NOT EXISTS UKOLY (
      ID INT AUTO_INCREMENT PRIMARY KEY,
      NAZEV VARCHAR(255) NOT NULL,
      POPIS TEXT NOT NULL,
      STAV VARCHAR(20) NOT NULL,
      DATUM_V DATE NOT NULL
  )''')

def pridat_ukol(cursor):
  nazev = input("Zadejte název úkolu: ")
  popis = input("Zadejte popis úkolu: ")
  stav = "Nezahájeno"
  datum_v = date.today()
  
  sql = "INSERT INTO UKOLY (NAZEV, POPIS, STAV, DATUM_V) VALUES (%s, %s, %s, %s)"
  val = (nazev, popis, stav, datum_v)
  cursor.execute(sql, val)
  print("Úkol byl úspěšně přidán.")
  
def ukazat_ukoly(cursor):
  cursor.execute("SELECT * FROM UKOLY")
  result = cursor.fetchall()
  if result:
    df = pd.DataFrame(result, columns=['ID', 'Název', 'Popis', 'Stav', 'Datum vytvoření'])
    print(df)
  else:
    return None

def zobrazit_ukoly(cursor):
  ukazat_ukoly(cursor)
  stav_filtr = input("Zadejte stav úkolu pro filtrování (Nezahájeno, Probíhá):")
  if stav_filtr:
    cursor.execute("SELECT * FROM UKOLY WHERE STAV = %s", (stav_filtr,))
    filtered_result = cursor.fetchall()
    if filtered_result:
      df_filtered = pd.DataFrame(filtered_result, columns=['ID', 'Název', 'Popis', 'Stav', 'Datum vytvoření'])
      print(df_filtered)
    else:
      print(f"Žádné úkoly se stavem '{stav_filtr}' k zobrazení.")


def aktualizovat_ukol(cursor):
  ukazat_ukoly(cursor)

  id_ukolu = input("Zadejte ID úkolu, který chcete aktualizovat: ")
  if id_ukolu is None or id_ukolu == "":
    print("Nesprávné zadání. Zadejte platné ID.")
    return
  novy_stav = input("Zadejte nový stav úkolu (Probíhá, Dokončeno): ")
  
  sql = "UPDATE UKOLY SET STAV = %s WHERE ID = %s"
  val = (novy_stav, id_ukolu)
  cursor.execute(sql, val)
  print("Úkol byl úspěšně aktualizován.")

def odstranit_ukol(cursor):
  ukazat_ukoly(cursor)
  
  id_ukolu = input("Zadejte ID úkolu, který chcete odstranit: ")
  if id_ukolu is None or id_ukolu == "":
    print("Nesprávné zadání. Zadejte platné ID.")
    return
  sql = "DELETE FROM UKOLY WHERE ID = %s"
  val = (id_ukolu,)
  cursor.execute(sql, val)
  print("Úkol byl úspěšně odstraněn.")

def main():

  dataBase = pripojeni_db()
  cursorObject = dataBase.cursor()
  cursorObject.execute ("CREATE DATABASE IF NOT EXISTS TASK_MAN")
  cursorObject.execute("USE TASK_MAN")
  vytvoreni_tabulky(cursorObject)
  volba = hlavni_menu()

  while volba != "5":
    if volba == "1":
      pridat_ukol(cursorObject)
    elif volba == "2":
      zobrazit_ukoly(cursorObject)
    elif volba == "3":
      aktualizovat_ukol(cursorObject)
    elif volba == "4":
      odstranit_ukol(cursorObject)
    else:
      print("Neplatná volba. Zadejte číslo 1-5.")
    volba = hlavni_menu()
  else:
    dataBase.commit()
    dataBase.close()
    print("Konec programu.")

if __name__ == "__main__":
  main()