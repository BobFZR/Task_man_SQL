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
      NAZEV VARCHAR(255) NOT NULL CHECK (LENGTH(NAZEV) > 0),
      POPIS TEXT NOT NULL CHECK (LENGTH(POPIS) > 0),
      STAV VARCHAR(20) NOT NULL,
      DATUM_V DATE NOT NULL
  )''')

def pridat_ukol_vstupy(cursor):
    nazev = ""
    while nazev == "":
      nazev = input("Zadejte název úkolu: ")
      if nazev == "":
        print("Název úkolu nemůže být prázdný.")
    popis = ""
    while popis == "":
      popis = input("Zadejte popis úkolu: ")
      if popis == "":
        print("Popis úkolu nemůže být prázdný.")
    stav = "Nezahájeno" 
    datum_v = date.today()
    
    pridat_ukol(cursor, nazev, popis, stav, datum_v)

def pridat_ukol(cursor, nazev, popis, stav, datum_v):
  try:      
      dtb = "INSERT INTO UKOLY (NAZEV, POPIS, STAV, DATUM_V) VALUES (%s, %s, %s, %s)"
      hodn = (nazev, popis, stav, datum_v)
      cursor.execute(dtb, hodn)
      print("Úkol byl úspěšně přidán.")
  except mysql.connector.Error as e:
      print(f"Nastala chyba při přidávání úkolu: {e}")
     

def ukazat_ukoly(cursor):
  try:
    cursor.execute("SELECT * FROM UKOLY")
    result = cursor.fetchall()
    if result:
      df = pd.DataFrame(result, columns=['ID', 'Název', 'Popis', 'Stav', 'Datum vytvoření'])
      print(df)
  except mysql.connector.Error as e:
    print(f"Nastala chyba při načítání údajů: {e}")
  else:
    return None


def zobrazit_ukoly(cursor):
  
  ukazat_ukoly(cursor)
  filtered_result = None
  
  stav_filtr = input("Zadejte stav úkolu pro filtrování (Nezahájeno, Probíhá):")
  if stav_filtr == "Nezahájeno" or stav_filtr == "Probíhá":
      cursor.execute("SELECT * FROM UKOLY WHERE STAV = %s", (stav_filtr,))
      filtered_result = cursor.fetchall()
      if filtered_result:
        df_filtered = pd.DataFrame(filtered_result, columns=['ID', 'Název', 'Popis', 'Stav', 'Datum vytvoření'])
        print(df_filtered)
      else:
        print(f"Žádné úkoly se stavem '{stav_filtr}' k zobrazení.")
  else:
       print("Nesprávné zadání podmínky filtru.")

def ukol_k_aktualizaci(cursor):
  ukazat_ukoly(cursor)
  cursor.execute("SELECT ID FROM UKOLY WHERE ID = (SELECT MAX(ID) FROM UKOLY);")
  maxid = cursor.fetchone()[-1]
  print(f"Maximální ID úkolu je: {maxid}")
  id_ukolu = ""
  while id_ukolu=="" or id_ukolu is None:
    id_ukolu = input("Zadejte ID úkolu, který chcete aktualizovat: ")
    if id_ukolu == "":
      print("Nesprávné zadání. Zadejte platné ID.")
    elif int(id_ukolu) < 1 or int(id_ukolu) >= maxid:
      print("Zadané ID neexistuje.")
      return
  novy_stav = ""   
  while novy_stav!="Probíhá" or novy_stav != "Dokončeno":
    novy_stav = input("Zadejte nový stav úkolu (Probíhá, Dokončeno): ")
    if novy_stav == "Probíhá" or novy_stav == "Dokončeno":
      break
   
  aktualizovat_ukol(cursor, id_ukolu, novy_stav)  

def aktualizovat_ukol(cursor, id_ukolu, novy_stav):
  
  try:
    dtb = "UPDATE UKOLY SET STAV = %s WHERE ID = %s"
    hodn = (novy_stav, id_ukolu)
    cursor.execute(dtb, hodn)
    print("Úkol byl úspěšně aktualizován.")
  except mysql.connector.Error as e:
    print(f"Nastala chyba při aktualizaci úkolu: {e}")

def ukol_k_odstraneni(cursor):
  ukazat_ukoly(cursor)
  id_ukolu = ""
  while id_ukolu=="" or id_ukolu is None:
    id_ukolu = input("Zadejte ID úkolu, který chcete odstranit: ")
    if id_ukolu == "":
      print("Nesprávné zadání. Zadejte platné ID.")
  odstranit_ukol(cursor, id_ukolu)

def odstranit_ukol(cursor, id_ukolu):
  try:  
    dtb = "DELETE FROM UKOLY WHERE ID = %s"
    hodn = (id_ukolu,)
    cursor.execute(dtb, hodn)
    print("Úkol byl úspěšně odstraněn.")
  except mysql.connector.Error as e:
    print(f"Nastala chyba při odstraňování úkolu: {e}")

def main():

  dataBase = pripojeni_db()
  cursorObject = dataBase.cursor()
  cursorObject.execute ("CREATE DATABASE IF NOT EXISTS TASK_MAN")
  cursorObject.execute("USE TASK_MAN")
  vytvoreni_tabulky(cursorObject)
  dataBase.commit()
  volba = hlavni_menu()

  while volba != "5":
    if volba == "1":
      pridat_ukol_vstupy(cursorObject)
      dataBase.commit()
    elif volba == "2":
      zobrazit_ukoly(cursorObject)
      dataBase.commit()
    elif volba == "3":
      ukol_k_aktualizaci(cursorObject)
      dataBase.commit()
    elif volba == "4":
      ukol_k_odstraneni(cursorObject)
      dataBase.commit()
    else:
      print("Neplatná volba. Zadejte číslo 1-5.")
    volba = hlavni_menu()
  else:
    dataBase.commit()
    dataBase.close()
    print("Konec programu.")

if __name__ == "__main__":
  main()