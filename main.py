import time

while True:
    def readEnergy():
        with open("/sys/class/powercap/intel-rapl:0/energy_uj", "r") as file:
            energy_uj = file.read()
            return(energy_uj)
    t1 = readEnergy()
    time.sleep(10)
    t2 = readEnergy()
    delta_t = int(t2) - int(t1)
    watts = delta_t / 10000000
    print(f"Power consumption: {watts} watts")
