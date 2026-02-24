from bs4 import BeautifulSoup

# Wczytaj plik HTML
with open("myhtml.html", "r", encoding="utf-8") as file:
    html_content = file.read()

# Parsowanie HTML
soup = BeautifulSoup(html_content, "html.parser")

# Pobranie danych z tabeli
table = soup.find("table")
rows = table.find_all("tr")[1:]  # Pomijamy nagłówek

# Przetworzenie i wydrukowanie danych
print("Extracted Data:")
for row in rows:
    cols = row.find_all("td")
    name = cols[0].text.strip()
    price = cols[1].text.strip()
    category = cols[2].text.strip()
    print(f"Name: {name}, Price: {price}, Category: {category}")