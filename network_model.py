import wntr

def create_network():
    wn = wntr.network.WaterNetworkModel()

    pobor_wzorzec = [
        0.1, 0.05, 0.05, 0.1, 0.3, 0.9,  # 00:00 - 05:00
        2.2, 2.8, 2.5, 1.5, 1.1, 0.8,  # 06:00 - 11:00
        0.7, 0.9, 1.2, 1.4, 1.8, 2.4,  # 12:00 - 17:00
        2.7, 2.3, 1.5, 0.8, 0.4, 0.2   # 18:00 - 23:00
    ]
    wn.add_pattern('dobowy', pobor_wzorzec)

    wn.add_reservoir('Zrodlo_Glowne', base_head=35, coordinates=(0,0))
    wn.add_junction('Rozdzielacz', base_demand=0, coordinates=(5,0))

    wn.add_junction('Dom_A', base_demand=0.004, demand_pattern='dobowy', coordinates=(10,5))
    wn.add_junction('Dom_B', base_demand=0.006, demand_pattern='dobowy', coordinates=(10,-5))
    
    wn.add_pipe('Rura_Glowna', 'Zrodlo_Glowne', 'Rozdzielacz', length=120, diameter=0.3, roughness=110)
    wn.add_pipe('Przylacz_A', 'Rozdzielacz', 'Dom_A', length=60, diameter=0.1, roughness=110)
    wn.add_pipe('Przylacz_B', 'Rozdzielacz', 'Dom_B', length=60, diameter=0.1, roughness=110)
    
    wn.options.time.duration = 24 * 3600       # 24 godziny symulacji
    wn.options.time.hydraulic_timestep = 1800  # Krok obliczeń hydraulicznych: 30 minut
    wn.options.time.pattern_timestep = 3600    # Krok zmiany wzorca: 1 godzina

    wn.options.time.report_timestep = 1800     
    
    wn.options.quality.parameter = 'AGE'

    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()

    print("Symulacja dobowa (24h - AGE) zakończona pomyślnie z krokiem raportowania 30 min.")
    return wn, results