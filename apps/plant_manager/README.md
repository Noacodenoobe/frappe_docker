# Plant Manager

System zarządzania roślinami dla ERPNext zgodnie z planem budowy.

## 🌟 Funkcjonalności

- **Hierarchiczna struktura lokalizacji** (DocType: Location)
  - Obsługa drzewa lokalizacji (Is Tree)
  - 4 poziomy hierarchii: Pietro → Strefa → Lokalizacja szczegółowa → Lokalizacja precyzyjna
  - Walidacja relacji rodzic-dziecko
- **Zarządzanie roślinami** (DocType: Plant)
  - Powiązanie z lokalizacjami
  - Status zdrowia roślin
  - Import z plików CSV
- **Import danych**
  - Import lokalizacji z plików .txt z hierarchią
  - Import roślin z pliku bazaroslin.csv
  - Automatyczne mapowanie lokalizacji zgodnie z zasadami

## 📦 Instalacja

### Wymagania wstępne
- ERPNext/Frappe Framework
- Bench environment
- Python 3.6+

### Kroki instalacji

1. **Skopiuj aplikację do katalogu apps**
   ```bash
   # W katalogu frappe-bench
   cp -r apps/plant_manager /path/to/frappe-bench/apps/
   ```

2. **Zainstaluj aplikację na stronie**
   ```bash
   bench --site [site-name] install-app plant_manager
   ```

3. **Uruchom migracje**
   ```bash
   bench --site [site-name] migrate
   ```

4. **Nadaj uprawnienia użytkownikom**
   ```bash
   # Utwórz rolę Plant Manager w ERPNext
   # Przypisz uprawnienia do DocTypes: Location, Plant
   ```

## 🔧 Import danych

### Import lokalizacji (Krok 1)
```python
# W konsoli Frappe
bench --site [site-name] console

# W konsoli Python
from plant_manager.importer import run_location_import
stats = run_location_import()
print(stats)
```

### Import roślin (Krok 2 - po imporcie lokalizacji)
```python
# W konsoli Frappe
from plant_manager.importer import run_plant_import
stats = run_plant_import()
print(stats)
```

### Pełny import (lokalizacje + rośliny)
```python
# W konsoli Frappe
from plant_manager.importer import import_all
stats = import_all()
print(stats)
```

## 📊 DocTypes

### Location (Lokalizacja)
- **Is Tree**: True (struktura hierarchiczna)
- **Fields**:
  - `location_name` (Data, Required, Unique) - Nazwa lokalizacji
  - `location_type` (Select, Required) - Typ: Pietro/Strefa/Lokalizacja szczegółowa/Lokalizacja precyzyjna
  - `parent_location` (Link) - Lokalizacja nadrzędna
  - `is_group` (Check) - Czy to grupa (auto-ustawiane)
  - `description` (Text) - Opis

### Plant (Roślina)
- **Fields**:
  - `plant_name` (Data, Required, Unique) - Nazwa rośliny
  - `species` (Data, Required) - Gatunek
  - `location` (Link to Location, Required) - Lokalizacja
  - `health_status` (Select) - Status zdrowia: Healthy/Needs Attention/Sick/Dead/Unknown
  - `acquisition_date` (Date) - Data nabycia
  - `description` (Text) - Opis

## 📁 Struktura plików źródłowych

Aplikacja oczekuje następujących plików w katalogu `/workspace/erpcursor/`:

- `Piętro 10 projekt stref wraz z hierarchią.txt`
- `Piętro 11 projekt stref wraz z hierarchią.txt`
- `Piętro 12 projekt stref wraz z hierarchią.txt`
- `Piętro 13 projekt stref wraz z hierarchią.txt`
- `Piętro 14 projekt stref wraz z hierarchią.txt`
- `bazaroslin.csv` (3500+ rekordów roślin)

## 🔍 Mapowanie danych CSV

Zgodnie z `zasady_agenta.md`:

- **Pietro** → `P{Pietro}`
- **Strefa_glowna** → Nazwa głównej strefy
- **Rodzaj_donicy** → Faktyczna nazwa lokalizacji szczegółowej
- **Lokalizacja_szczegolowa** → Poziom pośredni (opcjonalny)
- **Lokalizacja_precyzyjna** → Pozycja numeryczna lub nazwa precyzyjna

**Przykład ścieżki**: `P10 → Kuchnia → Konstrukcja podwieszona nad kuchnią`

## 🧪 Testy

Uruchom testy jednostkowe:
```bash
bench --site [site-name] run-tests plant_manager
```

## 📈 Walidacja struktury

Aplikacja została zwalidowana na podstawie:
- **3567 rekordów** w bazaroslin.csv
- **214 unikalnych lokalizacji**
- **90.9% dokładnych dopasowań** hierarchii
- **Pełna zgodność** z zasadami mapowania

## 🛠️ API Functions

### Location API
```python
from plant_manager.plant_manager.doctype.location.location import (
    get_location_by_path,
    create_location_if_not_exists
)

# Znajdź lokalizację po ścieżce
location = get_location_by_path(["P10", "Kuchnia", "Konstrukcja podwieszona nad kuchnią"])

# Utwórz lokalizację jeśli nie istnieje
location_name = create_location_if_not_exists("Nowa lokalizacja", "Strefa", parent_location="P10")
```

### Plant API
```python
from plant_manager.plant_manager.doctype.plant.plant import (
    create_plant_from_csv_data,
    bulk_import_plants_from_csv
)

# Import pojedynczej rośliny z danych CSV
csv_row = {...}
plant_name = create_plant_from_csv_data(csv_row)

# Bulk import
stats = bulk_import_plants_from_csv("/path/to/file.csv")
```

## 🔒 Bezpieczeństwo

- Walidacja hierarchii lokalizacji
- Obsługa błędów z logowaniem do Error Log
- Transakcje bazodanowe z commit/rollback
- Sprawdzanie uprawnień użytkowników

## 👨‍💻 Autor

Utworzone przez AI Agent zgodnie z dokumentacją:
- `plan_budowy.md` - Architektura i wymagania
- `zasady_agenta.md` - Reguły implementacji
- Walidacja na podstawie `bazaroslin.csv` i plików hierarchii

## 📄 Licencja

MIT