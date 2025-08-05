#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skrypt walidacyjny dla struktury lokalizacji roślin
Porównuje dane z pliku CSV z hierarchią z plików .txt
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
            
        # Oblicz poziom wcięcia
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
        
        # Określ poziom hierarchii (co 4 znaki wcięcia = 1 poziom)
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

def parsuj_csv_bazaroslin(plik_sciezka):
    """Parsuje plik CSV z danymi roślin"""
    unikalne_lokalizacje = set()
    statystyki = defaultdict(int)
    szczegoly = []
    
    with open(plik_sciezka, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            pietro = row['Pietro'].strip()
            strefa_glowna = row['Strefa_glowna'].strip()
            lokalizacja_szczegolowa = row['Lokalizacja_szczegolowa'].strip()
            lokalizacja_precyzyjna = row['Lokalizacja_precyzyjna'].strip()
            rodzaj_donicy = row['Rodzaj_donicy'].strip()
            
            # Buduj ścieżkę zgodnie z regułami
            elementy_sciezki = [f'P{pietro}']
            
            if strefa_glowna:
                elementy_sciezki.append(strefa_glowna)
            
            if lokalizacja_szczegolowa:
                elementy_sciezki.append(lokalizacja_szczegolowa)
            elif rodzaj_donicy and not lokalizacja_precyzyjna:
                # Jeśli nie ma lokalizacji szczegółowej, ale jest rodzaj donicy
                elementy_sciezki.append(rodzaj_donicy)
            
            if lokalizacja_precyzyjna:
                elementy_sciezki.append(lokalizacja_precyzyjna)
            
            sciezka_csv = ' -> '.join(elementy_sciezki)
            unikalne_lokalizacje.add(sciezka_csv)
            
            szczegoly.append({
                'pietro': pietro,
                'strefa_glowna': strefa_glowna, 
                'lokalizacja_szczegolowa': lokalizacja_szczegolowa,
                'lokalizacja_precyzyjna': lokalizacja_precyzyjna,
                'rodzaj_donicy': rodzaj_donicy,
                'sciezka_csv': sciezka_csv,
                'id_rosliny': row.get('ID_Rosliny', '')
            })
            
            statystyki[f'pietro_{pietro}'] += 1
            if strefa_glowna:
                statystyki[f'strefa_{strefa_glowna}'] += 1
    
    return unikalne_lokalizacje, statystyki, szczegoly

def porownaj_struktury(hierarchie_txt, lokalizacje_csv):
    """Porównuje struktury z .txt i CSV"""
    wszystkie_txt = set()
    for hierarchia in hierarchie_txt.values():
        wszystkie_txt.update(hierarchia.keys())
    
    # Znajdź rozbieżności
    tylko_w_txt = wszystkie_txt - lokalizacje_csv
    tylko_w_csv = lokalizacje_csv - wszystkie_txt
    wspolne = wszystkie_txt & lokalizacje_csv
    
    return {
        'tylko_w_txt': tylko_w_txt,
        'tylko_w_csv': tylko_w_csv,
        'wspolne': wspolne,
        'statystyki': {
            'txt_total': len(wszystkie_txt),
            'csv_total': len(lokalizacje_csv),
            'wspolne_total': len(wspolne)
        }
    }

def main():
    print("=== RAPORT WALIDACYJNY STRUKTURY LOKALIZACJI ===\n")
    
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
            print(f"Parsowanie {plik}...")
            hierarchie_txt[pietro_nr] = parsuj_hierarchie_txt(plik_sciezka)
        else:
            print(f"BŁĄD: Nie znaleziono pliku {plik_sciezka}")
    
    # 2. Parsuj dane CSV
    plik_csv = 'erpcursor/bazaroslin.csv'
    if os.path.exists(plik_csv):
        print(f"Parsowanie {plik_csv}...")
        lokalizacje_csv, statystyki_csv, szczegoly_csv = parsuj_csv_bazaroslin(plik_csv)
    else:
        print(f"BŁĄD: Nie znaleziono pliku {plik_csv}")
        return
    
    # 3. Wykonaj porównanie
    print("\n=== ANALIZA HIERARCHII Z PLIKÓW .TXT ===")
    for pietro, hierarchia in hierarchie_txt.items():
        print(f"\nPIĘTRO {pietro} ({len(hierarchia)} lokalizacji):")
        for sciezka in sorted(hierarchia.keys())[:10]:  # Pokaż pierwsze 10
            poziom = hierarchia[sciezka]['poziom']
            wcięcie = "  " * poziom
            print(f"{wcięcie}{hierarchia[sciezka]['nazwa']}")
        if len(hierarchia) > 10:
            print(f"  ... i {len(hierarchia) - 10} więcej")
    
    # 4. Analiza CSV
    print(f"\n=== ANALIZA DANYCH CSV ===")
    print(f"Znaleziono {len(lokalizacje_csv)} unikalnych lokalizacji w CSV")
    print(f"Przykładowe ścieżki CSV:")
    for sciezka in sorted(lokalizacje_csv)[:15]:
        print(f"  {sciezka}")
    
    # 5. Porównanie struktur
    print(f"\n=== PORÓWNANIE STRUKTUR ===")
    porownanie = porownaj_struktury(hierarchie_txt, lokalizacje_csv)
    
    print(f"Lokalizacje tylko w .txt: {len(porownanie['tylko_w_txt'])}")
    print(f"Lokalizacje tylko w CSV: {len(porownanie['tylko_w_csv'])}")
    print(f"Lokalizacje wspólne: {len(porownanie['wspolne'])}")
    
    if porownanie['tylko_w_csv']:
        print(f"\n=== LOKALIZACJE TYLKO W CSV (nie ma w .txt) ===")
        for sciezka in sorted(porownanie['tylko_w_csv'])[:20]:
            print(f"  ❌ {sciezka}")
    
    if porownanie['tylko_w_txt']:
        print(f"\n=== LOKALIZACJE TYLKO W .TXT (nie używane w CSV) ===")  
        for sciezka in sorted(porownanie['tylko_w_txt'])[:20]:
            print(f"  ⚠️  {sciezka}")
    
    print(f"\n=== PODSUMOWANIE ===")
    print(f"Problem: Struktura CSV nie odpowiada hierarchii .txt!")
    print(f"Wskaźnik zgodności: {len(porownanie['wspolne']) / max(len(lokalizacje_csv), 1) * 100:.1f}%")

if __name__ == "__main__":
    main()