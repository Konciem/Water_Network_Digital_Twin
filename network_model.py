import wntr

def create_network():
    wn = wntr.network.WaterNetworkModel()

    wn.add_reservoir('Zrodlo_Glowne', base_head=20, coordinates=(0,0))
    wn.add_junction('Rozdzielacz', base_demand=0, coordinates=(5,0))

    wn.add_junction('Dom_A', base_demand=0.002, coordinates=(10,5))
    wn.add_junction('Dom_B', base_demand=0.003, coordinates=(10,-5))

    wn.add_pipe('Rura_Glowna', 'Zrodlo_Glowne', 'Rozdzielacz', length=100, diameter=0.4, roughness=100)
    wn.add_pipe('Przylacz_A', 'Rozdzielacz', 'Dom_A', length=50, diameter=0.2, roughness=100)
    wn.add_pipe('Przylacz_B', 'Rozdzielacz', 'Dom_B', length=50, diameter=0.2, roughness=100)

    wn.options.time.duration = 3600
    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()

    print("Symulacja zakonczona pomyslnie.")
    return wn, results