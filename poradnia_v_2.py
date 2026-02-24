import requests

locations = {
    "Dominikanie": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=62&serviceId=6&serviceDuration=2700&providerIds[]=586&providerIds[]=49&extras=[]&group=1&page=booking&persons=1",
    "Fundacja towarzyszenia rodzinie": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=58&serviceId=6&serviceDuration=2700&providerIds[]=3648&providerIds[]=479&providerIds[]=85&providerIds[]=10163&providerIds[]=13346&providerIds[]=7848&providerIds[]=12167&providerIds[]=12165&providerIds[]=12168&extras=[]&group=1&page=booking&persons=1",
    "Opcatwo Cystersów w Mogile": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=12&serviceId=6&serviceDuration=2700&providerIds[]=86&providerIds[]=4825&extras=[]&group=1&page=booking&persons=1",
    "Ośrodek Katechumenalny przy kościele św. Marka": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=128&serviceId=6&serviceDuration=2700&providerIds[]=12164&extras=[]&group=1&page=booking&persons=1",
    "Parafia Bożego Ciała": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=23&serviceId=6&serviceDuration=2700&providerIds[]=121&extras=[]&group=1&page=booking&persons=1",
    "Parafia Matki Boskiej Ostrobramskiej": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=19&serviceId=6&serviceDuration=2700&providerIds[]=64&extras=[]&group=1&page=booking&persons=1",
    "Parafia Matki Bożej Różańcowej": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=14&serviceId=6&serviceDuration=2700&providerIds[]=120&extras=[]&group=1&page=booking&persons=1",
    "Parafia św. Floriana": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=25&serviceId=6&serviceDuration=2700&providerIds[]=586&extras=[]&group=1&page=booking&persons=1",
    "Parafia św. Jadwigi Królowej (Prądnik Biały)": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=59&serviceId=6&serviceDuration=2700&providerIds[]=79&extras=[]&group=1&page=booking&persons=1",
    "Parafia św. Jana Chrzciciela": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=22&serviceId=6&serviceDuration=2700&providerIds[]=12166&extras=[]&group=1&page=booking&persons=1",
    "Parafia św. Jana Kantego": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=9&serviceId=6&serviceDuration=2700&providerIds[]=4466&extras=[]&group=1&page=booking&persons=1",
    "Parafia św. Jana Pawła II (Biała Sala)": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=123&serviceId=6&serviceDuration=2700&providerIds[]=3648&providerIds[]=2640&providerIds[]=112&providerIds[]=479&providerIds[]=38&providerIds[]=104&extras=[]&group=1&page=booking&persons=1",
    "Arka Pana - Matki Bożej Królowej Polski (Bieńczyce)": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=122&serviceId=6&serviceDuration=2700&providerIds[]=97&extras=[]&group=1&page=booking&persons=1",
    "Parafia św. Judy Tadeusza": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=63&serviceId=6&serviceDuration=2700&providerIds[]=93&extras=[]&group=1&page=booking&persons=1",
    "Parafia św. Józefa Oblubieńca": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=5&serviceId=6&serviceDuration=2700&providerIds[]=40&extras=[]&group=1&page=booking&persons=1",
    "Parafia św. Maksymiliana": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=33&serviceId=6&serviceDuration=2700&providerIds[]=97&extras=[]&group=1&page=booking&persons=1",
    "Parafia Najświętszej Rodziny": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=8&serviceId=6&serviceDuration=2700&providerIds[]=3317&extras=[]&group=1&page=booking&persons=1",
    "Parafia Miłosierdzia Bożego": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=7&serviceId=6&serviceDuration=2700&providerIds[]=46&extras=[]&group=1&page=booking&persons=1",
    "Parafia Matki Boskiej Częstochowskiej": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=13&serviceId=6&serviceDuration=2700&providerIds[]=60&extras=[]&group=1&page=booking&persons=1",
    "Parafia Matki Bożej Dobrej Rady": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=6&serviceId=6&serviceDuration=2700&providerIds[]=67&extras=[]&group=1&page=booking&persons=1",
    "Parafia Najświętszego Serca Jezusowego (ul. Saska)": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=40&serviceId=6&serviceDuration=2700&providerIds[]=59&extras=[]&group=1&page=booking&persons=1",
    "Szklane Domy": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=46&serviceId=6&serviceDuration=2700&providerIds[]=74&extras=[]&group=1&page=booking&persons=1",
    "Parafia Zmartwychwstania Pańskiego": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=46&serviceId=6&serviceDuration=2700&providerIds[]=74&extras=[]&group=1&page=booking&persons=1",
    "Parafia Miłosierdzia Bożego (nowa)": "https://ftrodzinie.pl/wp-admin/admin-ajax.php?action=wpamelia_api&call=/slots&locationId=130&serviceId=6&serviceDuration=2700&providerIds[]=12166&extras=[]&group=1&page=booking&persons=1",
}

available_slots_map = {}

for name, url in locations.items():
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "slots" in data.get("data", {}) and data["data"]["slots"]:
            available_slots_map[name] = data["data"]["slots"]
    except requests.RequestException as e:
        print(f"Błąd przy pobieraniu danych z {name}: {e}")
    except ValueError:
        print(f"Niepoprawny JSON z {name}")

# Ładne wypisanie wyników
print("\nDostępne terminy:\n")
for name, slots in available_slots_map.items():
    print(f"📍 {name}")
    for date, hours in slots.items():
        for hour, details in hours.items():
            provider_id = details[0][0] if details and details[0] else "?"
            # print(f"  📅 {date} ⏰ {hour} (provider: {provider_id})")
            print(f"  📅 {date} ⏰ {hour}")
    print("-" * 50)

# https://ftrodzinie.pl/zapisy-narzeczeni/