import time
import requests

while True:
    def readEnergy(): # reads instantateous energy consumption in microjoules
        with open("/sys/class/powercap/intel-rapl:0/energy_uj", "r") as file:
            energy_uj = file.read()
            return(energy_uj)
    
    def readMaxEnergy(): # reads maximum energy consumption in microjoules
        with open("/sys/class/powercap/intel-rapl:0/max_energy_range_uj", "r") as file:
            max_energy = file.read()
            return(max_energy)

    def energyUsed(start, end, max_energy): # calculates delta energy, accounting for wrap around
        if (start>end): # if t1>t2, it means the energy counter has wrapped around
            return (max_energy - int(start) + int(end))
        return (int(end) - int(start))

    start = readEnergy()
    time.sleep(10)
    end = readEnergy()
    delta_e = energyUsed(start, end, readMaxEnergy())
    watts = delta_e / 10000000
    print(f"Power consumption: {watts} watts")
    print(f"Energy consumption: {delta_e} microjoules")
    print(f"Max energy consumption: {readMaxEnergy()} microjoules")
