import time

while True:
    def readEnergy(): # reads instantateous energy consumption in microjoules
        with open("/sys/class/powercap/intel-rapl:0/energy_uj", "r") as file:
            energy_uj = file.read()
            return(energy_uj)
    
    def readMaxEnergy(): # reads maximum energy consumption in microjoules
        with open("/sys/class/powercap/intel-rapl:0/max_energy_range_uj", "r") as file:
            max_energy = file.read()
            return(max_energy)

    def energyUsed(min, max, max_energy): # calculates delta energy, accounting for wrap around
        if (min>max): # if t1>t2, it means the energy counter has wrapped around
            return (max_energy - int(min) + int(max))
        return (int(max) - int(min))

    min = readEnergy()
    time.sleep(10)
    max = readEnergy()
    delta_e = energyUsed(min, max, readMaxEnergy())
    watts = delta_e / 10000000
    print(f"Power consumption: {watts} watts")
    