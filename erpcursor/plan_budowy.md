# Plan Budowy: Moduł Zarządzania Roślinami dla Agenta AI

## 1. Cel Główny

Twoim zadaniem jest stworzenie w pełni funkcjonalnego modułu do zarządzania roślinami w systemie ERPNext. Moduł musi być zaimplementowany jako nowa, niestandardowa aplikacja Frappe. Kluczowe jest precyzyjne odwzorowanie złożonej, hierarchicznej struktury lokalizacji dostarczonej w plikach tekstowych oraz stworzenie powiązanego systemu do ewidencji roślin. Projekt składa się z dwóch etapów: budowy struktury i późniejszego importu danych o roślinach.

---

## 2. Architektura Danych (DocTypes)

Musisz stworzyć dwa nowe, kluczowe typy dokumentów (DocTypes) wewnątrz nowej aplikacji.

### 2.1. DocType: Lokalizacja (`Location`)

*   **Nazwa w kodzie:** `Location`
*   **Nazwa w UI:** `Lokalizacja`
*   **Opcje:** Musi być oznaczony jako **"Is Tree"**.
*   **Pola (Fields):**
    *   `location_name` (Label: 'Nazwa Lokalizacji', Type: Data, Required: 1)
    *   `parent_location` (Label: 'Lokalizacja Nadrzędna', Type: Link, Options: 'Location')
    *   `is_group` (Label: 'Is Group', Type: Check)

### 2.2. DocType: Roślina (`Plant`)

*   **Nazwa w kodzie:** `Plant`
*   **Nazwa w UI:** `Roślina`
*   **Opcje:** Autoname: `field:plant_id`, Title Field: `plant_name`.
*   **Pola (Fields):**
    *   `plant_id` (Label: 'ID Rośliny', Type: Data, Unique: 1, Required: 1)
    *   `plant_name` (Label: 'Nazwa Rośliny', Type: Data)
    *   `location` (Label: 'Lokalizacja', Type: Link, Options: 'Location', Required: 1)
    *   `pot_type` (Label: 'Rodzaj Donicy', Type: Data)
    *   `status` (Label: 'Status', Type: Select, Options: \nZdrowa\nWymaga uwagi\nSzkodnik)
    *   `photo` (Label: 'Zdjęcie', Type: Attach Image)
    *   `notes` (Label: 'Notatki', Type: Text)

---

## 3. Plan Działania dla Agenta (Etap 1: Budowa Struktury)

Wykonaj poniższe zadania w ścisłej kolejności.

### Krok A: Stwórz Aplikację
*   **Komenda:** `bench new-app plant_manager`

### Krok B: Zaimplementuj DocType `Location`
*   Stwórz pliki definicyjne dla DocType `Location` zgodnie ze specyfikacją z sekcji 2.1.

### Krok C: Zaimplementuj DocType `Plant`
*   Stwórz pliki definicyjne dla DocType `Plant` zgodnie ze specyfikacją z sekcji 2.2.

### Krok D: Stwórz Skrypt Importujący Lokalizacje
*   W aplikacji `plant_manager` stwórz plik `importer.py`.
*   Napisz w nim funkcję `run_location_import()`, która:
    1.  Przetworzy 5 plików .txt z hierarchią.
    2.  Przeanalizuje wcięcia, aby zrozumieć relacje rodzic-dziecko.
    3.  Stworzy w bazie danych wszystkie dokumenty `Location` z poprawnie ustawionymi powiązaniami.

### Krok E: Zakończ Instalację i Uruchom Import Lokalizacji
1.  Zainstaluj aplikację: `bench --site localhost install-app plant_manager`
2.  Uruchom skrypt importujący lokalizacje: `bench --site localhost execute "plant_manager.importer.run_location_import"`
3.  Zastosuj zmiany w bazie: `bench --site localhost migrate`

---

## 4. Strategia Importu Danych o Roślinach (Etap 2 - do wykonania w przyszłości)

Po zakończeniu Etapu 1, system będzie gotowy na przyjęcie danych o roślinach. Proces ten będzie wymagał stworzenia drugiego skryptu, który zmapuje dane z pliku CSV na nową strukturę bazy danych. Na tym etapie nie musisz go implementować, ale miej świadomość tej architektury.