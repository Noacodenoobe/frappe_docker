# Zasady Pracy dla Agenta AI

Musisz przestrzegać tych zasad podczas całej swojej pracy nad tym projektem.

1.  **Język i Komentarze:** Cały kod pisz w języku Python 3. Wszystkie komentarze w kodzie, nazwy zmiennych (jeśli to możliwe) oraz komunikaty dla użytkownika pisz w języku **polskim**.
2.  **Konwencje Frappe Framework:** Ściśle przestrzegaj konwencji kodowania i struktury projektu obowiązujących w Frappe. Używaj wbudowanych funkcji API (`frappe.get_doc`, `frappe.db.exists`, `frappe.log_error` itp.), zamiast tworzyć własne odpowiedniki.
3.  **Myśl Krok po Kroku:** Przed wykonaniem każdej złożonej operacji (zwłaszcza przed napisaniem skryptu `importer.py`), przedstaw w zwięzły sposób swój plan na jej realizację.
4.  **Nie Wymyślaj:** Twoim jedynym źródłem prawdy o wymaganiach jest plik `plan_budowy.md`. Nie dodawaj żadnych funkcji ani pól, które nie są w nim zdefiniowane. Jeśli czegoś nie wiesz lub instrukcja jest niejasna, zadaj pytanie, zamiast zakładać.
5.  **Obsługa Błędów:** W skrypcie importującym zaimplementuj podstawową obsługę błędów (np. blok `try...except`) i loguj ewentualne problemy za pomocą `frappe.log_error`, aby można było je później zdiagnozować.
6.  **Czystość Kodu:** Pisz czytelny, dobrze sformatowany kod.
7. **Mapowanie lokalizacji przy imporcie roślin**: W pliku CSV z danymi roślin kolumny Pietro, Strefa_glowna, Lokalizacja_szczegolowa oraz Lokalizacja_precyzyjna opisują pełną ścieżkę lokalizacji. Podczas importu roślin:

- Ignoruj kolumnę lp – jest to tylko licznik wierszy.

- Wyznacz ścieżkę poprzez połączenie wartości tych kolumn w kolejności: Pietro → Strefa_glowna → Lokalizacja_szczegolowa → Lokalizacja_precyzyjna.

- Znajdź istniejący węzeł Location odpowiadający tej ścieżce. Jeśli węzeł nie istnieje, zgłoś błąd lub utwórz go zgodnie z logiką importu lokalizacji.

- Ustaw pole location w dokumencie Plant tak, aby wskazywało na odnaleziony węzeł drzewa lokalizacji. Nie przechowuj powyższych pól oddzielnie w Plant, gdyż drzewo Location reprezentuje je w sposób jednoznaczny.

- Pamiętaj, że plik CSV jest rozdzielany średnikami (;), a pierwszy wiersz zawiera nagłówki.