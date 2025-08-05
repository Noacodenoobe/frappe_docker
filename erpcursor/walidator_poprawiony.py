#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POPRAWIONY skrypt walidacyjny dla struktury lokalizacji roślin
Uwzględnia rzeczywiste mapowanie kolumn CSV
"""

import csv
import os
import re
from collections import defaultdict

def parsuj_hierarchie_txt(plik_sciezka):
    """Parsuje plik hierarchii .txt i zwraca drzewo lokalizacji"""
    hierarchia = {}
    stos_poziomow = []
    
    with open(plik_sciezka, 'r', encoding='utf-8') as f:
        linie = f.readlines()
    
    for linia in linie:
        linia_oryginalna = linia.rstrip()
        if not linia_oryginalna:
            continue
            
        # Oblicz poziom wcięcia (każde 4 znaki = 1 poziom)
        poziom = 0
        for char in linia_oryginalna:
            if char in ['├', '│', '└', '─', ' ']:
                poziom += 1
            else:
                break
        
        # Wyciągnij nazwę lokalizacji
        nazwa = linia_oryginalna[poziom:].strip()
        if not nazwa or nazwa.startswith(('├', '└', '│')):
            continue
        
        # Usuń znaki drzewa z nazwy
        nazwa = re.sub(r'^[├└│─\s]+', '', nazwa).strip()
        if not nazwa:
            continue
        
        poziom_hierarchii = poziom // 4
        
        # Zaktualizuj stos poziomów
        stos_poziomow = stos_poziomow[:poziom_hierarchii]
        stos_poziomow.append(nazwa)
        
        # Zapisz pełną ścieżkę
        sciezka_pelna = ' -> '.join(stos_poziomow)
        if sciezka_pelna not in hierarchia:
            hierarchia[sciezka_pelna] = {
                'poziom': poziom_hierarchii,
                'nazwa': nazwa,
                'sciezka': stos_poziomow.copy(),
                'rodzic': ' -> '.join(stos_poziomow[:-1]) if len(stos_poziomow) > 1 else None
            }
    
    return hierarchia

def normalizuj_nazwe(nazwa):
    """Normalizuje nazwę dla porównania (wielkość liter itp.)"""
    if not nazwa:
        return ""
    # Pierwsza litera wielka, reszta bez zmian
    return nazwa[0].upper() + nazwa[1:] if len(nazwa) > 1 else nazwa.upper()

def parsuj_csv_bazaroslin_poprawnie(plik_sciezka):
    """Parsuje plik CSV z POPRAWNYM mapowaniem kolumn"""
    unikalne_lokalizacje = set()
    statystyki = defaultdict(int)
    szczegoly = []
    problemy = []
    
    with open(plik_sciezka, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for row_num, row in enumerate(reader, 1):
            pietro = row['Pietro'].strip()
            strefa_glowna = row['Strefa_glowna'].strip()
            lokalizacja_szczegolowa = row['Lokalizacja_szczegolowa'].strip()
            lokalizacja_precyzyjna = row['Lokalizacja_precyzyjna'].strip()
            rodzaj_donicy = row['Rodzaj_donicy'].strip()  # To jest faktyczna lokalizacja!
            
            # POPRAWNE mapowanie zgodnie z rzeczywistymi danymi:
            # Pietro -> Strefa_glowna -> Rodzaj_donicy (to lokalizacja!) -> Lokalizacja_precyzyjna (pozycja)
            
            elementy_sciezki = [f'P{pietro}']
            
            # Normalizuj nazwy stref
            if strefa_glowna:
                strefa_normalized = normalizuj_nazwe(strefa_glowna)
                elementy_sciezki.append(strefa_normalized)
            
            # Rodzaj_donicy to faktycznie lokalizacja szczegółowa
            if rodzaj_donicy:
                elementy_sciezki.append(rodzaj_donicy)
            
            # Lokalizacja_szczegolowa - jeśli istnieje, dodaj jako poziom pośredni
            if lokalizacja_szczegolowa:
                # Wstaw przed ostatnim elementem jeśli rodzaj_donicy istnieje
                if rodzaj_donicy:
                    elementy_sciezki.insert(-1, lokalizacja_szczegolowa)
                else:
                    elementy_sciezki.append(lokalizacja_szczegolowa)
            
            # Lokalizacja_precyzyjna - tylko jeśli nie jest liczbą (liczby = pozycje)
            if lokalizacja_precyzyjna and not lokalizacja_precyzyjna.isdigit():
                elementy_sciezki.append(lokalizacja_precyzyjna)
            
            sciezka_csv = ' -> '.join(elementy_sciezki)
            unikalne_lokalizacje.add(sciezka_csv)
            
            # Dodaj szczegóły dla debugowania
            szczegol = {
                'row_num': row_num,
                'pietro': pietro,
                'strefa_glowna': strefa_glowna,
                'lokalizacja_szczegolowa': lokalizacja_szczegolowa,
                'lokalizacja_precyzyjna': lokalizacja_precyzyjna,
                'rodzaj_donicy': rodzaj_donicy,
                'sciezka_csv': sciezka_csv,
                'id_rosliny': row.get('ID_Rosliny', '')
            }
            szczegoly.append(szczegol)
            
            # Sprawdź czy lokalizacja_precyzyjna to liczba
            if lokalizacja_precyzyjna.isdigit():
                szczegol['pozycja_numeryczna'] = True
            
            statystyki[f'pietro_{pietro}'] += 1
            if strefa_glowna:
                statystyki[f'strefa_{strefa_glowna}'] += 1
            if rodzaj_donicy:
                statystyki[f'lokalizacja_{rodzaj_donicy}'] += 1
    
    return unikalne_lokalizacje, statystyki, szczegoly, problemy

def porownaj_struktury_szczegolowo(hierarchie_txt, lokalizacje_csv, szczegoly_csv):
    """Szczegółowe porównanie struktur z analizą podobieństw"""
    wszystkie_txt = set()
    for hierarchia in hierarchie_txt.values():
        wszystkie_txt.update(hierarchia.keys())
    
    # Znajdź dokładne dopasowania
    dokladne_dopasowania = wszystkie_txt & lokalizacje_csv
    
    # Znajdź podobne (częściowe dopasowania)
    podobne_dopasowania = []
    for csv_sciezka in lokalizacje_csv:
        if csv_sciezka not in dokladne_dopasowania:
            for txt_sciezka in wszystkie_txt:
                # Sprawdź czy ścieżki są podobne
                csv_elementy = csv_sciezka.split(' -> ')
                txt_elementy = txt_sciezka.split(' -> ')
                
                # Podobieństwo gdy zawiera te same elementy
                wspolne_elementy = set(csv_elementy) & set(txt_elementy)
                if len(wspolne_elementy) >= 2:  # Przynajmniej 2 wspólne elementy
                    podobne_dopasowania.append({
                        'csv': csv_sciezka,
                        'txt': txt_sciezka,
                        'wspolne': wspolne_elementy,
                        'podobienstwo': len(wspolne_elementy) / max(len(csv_elementy), len(txt_elementy))
                    })
    
    return {
        'tylko_w_txt': wszystkie_txt - lokalizacje_csv,
        'tylko_w_csv': lokalizacje_csv - wszystkie_txt,
        'dokladne_dopasowania': dokladne_dopasowania,
        'podobne_dopasowania': podobne_dopasowania,
        'statystyki': {
            'txt_total': len(wszystkie_txt),
            'csv_total': len(lokalizacje_csv),
            'dokladne_total': len(dokladne_dopasowania),
            'podobne_total': len(podobne_dopasowania)
        }
    }

def main():
    print("=== POPRAWIONY RAPORT WALIDACYJNY STRUKTURY LOKALIZACJI ===\n")
    
    # 1. Parsuj hierarchie z plików .txt
    pliki_txt = [
        'Piętro 10 projekt stref wraz z hierarchią.txt',
        'Piętro 11 projekt stref wraz z hierarchią.txt', 
        'Piętro 12 projekt stref wraz z hierarchią.txt',
        'Piętro 13 projekt stref wraz z hierarchią.txt',
        'Piętro 14 projekt stref wraz z hierarchią.txt'
    ]
    
    hierarchie_txt = {}
    for plik in pliki_txt:
        plik_sciezka = f'erpcursor/{plik}'
        if os.path.exists(plik_sciezka):
            pietro_nr = plik.split(' ')[1]
            print(f"📄 Parsowanie {plik}...")
            hierarchie_txt[pietro_nr] = parsuj_hierarchie_txt(plik_sciezka)
        else:
            print(f"❌ BŁĄD: Nie znaleziono pliku {plik_sciezka}")
    
    # 2. Parsuj dane CSV z poprawnym mapowaniem
    plik_csv = 'erpcursor/bazaroslin.csv'
    if os.path.exists(plik_csv):
        print(f"📄 Parsowanie {plik_csv} z poprawnym mapowaniem...")
        lokalizacje_csv, statystyki_csv, szczegoly_csv, problemy = parsuj_csv_bazaroslin_poprawnie(plik_csv)
    else:
        print(f"❌ BŁĄD: Nie znaleziono pliku {plik_csv}")
        return
    
    # 3. Szczegółowa analiza CSV
    print(f"\n=== ANALIZA POPRAWNEGO MAPOWANIA CSV ===")
    print(f"📊 Znaleziono {len(lokalizacje_csv)} unikalnych lokalizacji w CSV")
    print(f"📊 Przeanalizowano {len(szczegoly_csv)} rekordów roślin")
    
    # Statystyki pozycji numerycznych
    pozycje_numeryczne = sum(1 for s in szczegoly_csv if s.get('pozycja_numeryczna', False))
    print(f"📊 Pozycji numerycznych (1,2,3...): {pozycje_numeryczne}")
    
    print(f"\n🔍 Przykładowe POPRAWNIE zmapowane ścieżki CSV:")
    for i, sciezka in enumerate(sorted(lokalizacje_csv)[:10]):
        print(f"  ✅ {sciezka}")
    
    # 4. Szczegółowe porównanie
    print(f"\n=== SZCZEGÓŁOWE PORÓWNANIE STRUKTUR ===")
    porownanie = porownaj_struktury_szczegolowo(hierarchie_txt, lokalizacje_csv, szczegoly_csv)
    
    print(f"📊 Dokładne dopasowania: {len(porownanie['dokladne_dopasowania'])}")
    print(f"📊 Podobne dopasowania: {len(porownanie['podobne_dopasowania'])}")
    print(f"📊 Tylko w .txt: {len(porownanie['tylko_w_txt'])}")
    print(f"📊 Tylko w CSV: {len(porownanie['tylko_w_csv'])}")
    
    if porownanie['dokladne_dopasowania']:
        print(f"\n✅ DOKŁADNE DOPASOWANIA:")
        for dopasowanie in sorted(porownanie['dokladne_dopasowania'])[:10]:
            print(f"  ✅ {dopasowanie}")
    
    if porownanie['podobne_dopasowania']:
        print(f"\n🔍 PODOBNE DOPASOWANIA (wymagają weryfikacji):")
        for podobne in sorted(porownanie['podobne_dopasowania'], 
                             key=lambda x: x['podobienstwo'], reverse=True)[:10]:
            print(f"  🔄 CSV: {podobne['csv']}")
            print(f"     TXT: {podobne['txt']}")
            print(f"     Podobieństwo: {podobne['podobienstwo']:.1%}\n")
    
    if porownanie['tylko_w_csv']:
        print(f"\n❌ LOKALIZACJE TYLKO W CSV (brak w hierarchii .txt):")
        for sciezka in sorted(porownanie['tylko_w_csv'])[:15]:
            print(f"  ❌ {sciezka}")
    
    # 5. Końcowy raport
    wszystkie_dopasowania = len(porownanie['dokladne_dopasowania']) + len(porownanie['podobne_dopasowania'])
    wskaznik_zgodnosci = wszystkie_dopasowania / max(len(lokalizacje_csv), 1) * 100
    
    print(f"\n=== PODSUMOWANIE WALIDACJI ===")
    print(f"🎯 Wskaźnik zgodności (doładne + podobne): {wskaznik_zgodnosci:.1f}%")
    print(f"🎯 Dokładne dopasowania: {len(porownanie['dokladne_dopasowania']) / max(len(lokalizacje_csv), 1) * 100:.1f}%")
    
    if wskaznik_zgodnosci < 80:
        print(f"⚠️  UWAGA: Niska zgodność! Wymagane korekty w strukturze hierarchii.")
    else:
        print(f"✅ Struktura w większości poprawna!")
    
    return porownanie, szczegoly_csv

if __name__ == "__main__":
    main()