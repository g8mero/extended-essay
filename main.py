def readEnergy():
    with open("/sys/class/powercap/intel-rapl:0/energy_uj", "r") as file:
        energy_uj = file.read()
        return(energy_uj)
print(readEnergy())