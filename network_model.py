import wntr

def create_network():
    wn = wntr.network.WaterNetworkModel()

    # 1. WZORZEC DOMOWY (Szczyt poranny i wieczorny)
    wzorzec_dom = [
        0.2, 0.1, 0.1, 0.2, 0.5, 1.2,  # 00:00 - 05:00
        2.5, 3.0, 2.2, 1.5, 1.2, 1.0,  # 06:00 - 11:00
        0.9, 1.1, 1.4, 1.8, 2.3, 2.8,  # 12:00 - 17:00
        3.2, 2.5, 1.6, 0.9, 0.5, 0.3   # 18:00 - 23:00
    ]
    wn.add_pattern('domowy', wzorzec_dom)

    # 2. WZORZEC PRZEMYSŁOWY (Praca w godzinach 8:00 - 16:00)
    wzorzec_przemysl = [
        0.0, 0.0, 0.0, 0.0, 0.0, 0.2,  # 00:00 - 05:00
        0.8, 2.5, 3.5, 3.5, 3.5, 3.5,  # 06:00 - 11:00
        3.5, 3.5, 3.0, 2.0, 0.8, 0.2,  # 12:00 - 17:00
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0   # 18:00 - 23:00
    ]
    wn.add_pattern('przemyslowy', wzorzec_przemysl)

    # --- WĘZŁY (JUNCTIONS / RESERVOIRS / TANKS) ---
    
    # Źródło zasilania (Base Head = 45m dla lepszego ciśnienia w rozbudowanej sieci)
    wn.add_reservoir('Zrodlo_Glowne', base_head=45, coordinates=(0, 0))
    
    # Główne punkty tranzytowe (Brak poboru własnego)
    wn.add_junction('Rozdzielacz_Zachod', base_demand=0, coordinates=(4, 2))
    wn.add_junction('Rozdzielacz_Wschod', base_demand=0, coordinates=(8, 2))
    wn.add_junction('Wezel_Centralny', base_demand=0, coordinates=(6, -2))

    # Strefa Mieszkalna A (Wzorzec domowy)
    wn.add_junction('Osiedle_A1', base_demand=0.005, demand_pattern='domowy', coordinates=(3, 5))
    wn.add_junction('Osiedle_A2', base_demand=0.004, demand_pattern='domowy', coordinates=(5, 5))
    
    # Strefa Mieszkalna B (Wzorzec domowy)
    wn.add_junction('Domki_B1', base_demand=0.006, demand_pattern='domowy', coordinates=(10, 4))
    wn.add_junction('Domki_B2', base_demand=0.005, demand_pattern='domowy', coordinates=(12, 2))

    # Strefa Przemysłowa (Wzorzec przemysłowy - duże, skokowe zmiany rozbioru)
    wn.add_junction('Fabryka_P1', base_demand=0.015, demand_pattern='przemyslowy', coordinates=(5, -6))
    wn.add_junction('Strefa_Tech_P2', base_demand=0.010, demand_pattern='przemyslowy', coordinates=(8, -6))

    # Kropka nad "i": Dynamiczny zbiornik wieżowy (Napełnia się i opróżnia)
    # tank_wyz = rzędna dna, init_level = pocz. poziom wody, min/max_level = zakres, diam = średnica zbiornika
    wn.add_tank('Wieza_Cisnien', elevation=25, init_level=4, min_level=1, max_level=6, diameter=8, coordinates=(11, -2))

    # --- RUROCIĄGI (PIPES) ---
    
    # Główne magistrale zasilające (większa średnica)
    wn.add_pipe('Magistrala_1', 'Zrodlo_Glowne', 'Rozdzielacz_Zachod', length=150, diameter=0.30, roughness=120)
    wn.add_pipe('Magistrala_2', 'Rozdzielacz_Zachod', 'Rozdzielacz_Wschod', length=100, diameter=0.25, roughness=120)
    wn.add_pipe('Magistrala_3', 'Rozdzielacz_Zachod', 'Wezel_Centralny', length=120, diameter=0.25, roughness=120)
    
    # Przepust do zbiornika wieżowego
    wn.add_pipe('Nitka_Zbiornika', 'Rozdzielacz_Wschod', 'Wieza_Cisnien', length=80, diameter=0.20, roughness=120)
    wn.add_pipe('Spinka_Dolna', 'Wezel_Centralny', 'Wieza_Cisnien', length=140, diameter=0.15, roughness=110)

    # Sieć rozdzielcza - Osiedle A
    wn.add_pipe('Rura_Osiedle_A1', 'Rozdzielacz_Zachod', 'Osiedle_A1', length=60, diameter=0.10, roughness=110)
    wn.add_pipe('Rura_Osiedle_A2', 'Osiedle_A1', 'Osiedle_A2', length=50, diameter=0.08, roughness=110)
    wn.add_pipe('Rura_Zamkniecia_A', 'Osiedle_A2', 'Rozdzielacz_Wschod', length=60, diameter=0.08, roughness=110)

    # Sieć rozdzielcza - Domki B
    wn.add_pipe('Rura_Domki_B1', 'Rozdzielacz_Wschod', 'Domki_B1', length=70, diameter=0.10, roughness=110)
    wn.add_pipe('Rura_Domki_B2', 'Domki_B1', 'Domki_B2', length=50, diameter=0.08, roughness=110)

    # Sieć rozdzielcza - Przemysł
    wn.add_pipe('Rura_Przemysl_1', 'Wezel_Centralny', 'Fabryka_P1', length=90, diameter=0.15, roughness=100)
    wn.add_pipe('Rura_Przemysl_2', 'Fabryka_P1', 'Strefa_Tech_P2', length=80, diameter=0.12, roughness=100)

    # --- PARAMETRY SYMULACJI ---
    wn.options.time.duration = 24 * 3600       # 24 godziny symulacji
    wn.options.time.hydraulic_timestep = 1800  # Krok hydrauliki: 30 minut
    wn.options.time.pattern_timestep = 3600    # Zmiana rozbioru: 1 godzina
    wn.options.time.report_timestep = 1800     # Raport: 30 minut
    
    wn.options.quality.parameter = 'AGE'       # Badanie wieku wody

    # Uruchomienie symulacji Epanet
    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()

    print(f"Zaawansowana symulacja zakończona sukcesem. Wygenerowano {len(wn.junction_name_list)} węzłów i {len(wn.tank_name_list)} zbiornik.")
    return wn, results