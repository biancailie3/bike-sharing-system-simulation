# logic.py
import simpy
import random

# Parametri impliciți (pot fi suprascriși de interfață)
DAY_LENGTH = 720 # 12 ore

# Clasele tale (nemodificate ca logică)
class BikeStation:
    # Am adaugat lat si lon aici in paranteza
    def __init__(self, name, capacity, init_bikes, lat, lon):
        self.name = name
        self.capacity = capacity
        self.bikes = init_bikes
        self.lat = lat  # Salvăm latitudinea
        self.lon = lon  # Salvăm longitudinea
        self.level_history = [] 

    def rent_bike(self):
        if self.bikes > 0:
            self.bikes -= 1
            return True
        return False

    def return_bike(self):
        if self.bikes < self.capacity:
            self.bikes += 1
            return True
        return False
    
    def log_status(self):
        self.level_history.append(self.bikes)
class BikeSharingSystem:
    def __init__(self, env, stations, rebalance_interval):
        self.env = env
        self.stations = stations
        self.rebalance_interval = rebalance_interval
        
        # Statistici
        self.unhappy_no_bike = 0
        self.unhappy_no_space = 0
        self.broken_bikes = 0
        
        # Pornim procesele
        self.env.process(self.customer_generator())
        self.env.process(self.rebalancer())

    def customer_generator(self):
        while True:
            # Vin clienți la intervale random
            yield self.env.timeout(random.expovariate(1/5))
            self.env.process(self.handle_customer())

    def handle_customer(self):
        start_station = random.choice(self.stations)
        end_station = random.choice([s for s in self.stations if s != start_station])

        # Încearcă să închirieze
        if not start_station.rent_bike():
            self.unhappy_no_bike += 1
            return

        # Călătoria durează între 10 și 30 min
        yield self.env.timeout(random.randint(10, 30))

        # Încearcă să returneze
        if not end_station.return_bike():
            self.unhappy_no_space += 1

    def rebalancer(self):
        # Camionul care mută biciclete
        while True:
            yield self.env.timeout(self.rebalance_interval)
            # Logica ta simplă: calculează media și mută
            avg = sum(s.bikes for s in self.stations) / len(self.stations)
            for s in self.stations:
                if s.bikes > avg + 1:
                    deficit_stations = [x for x in self.stations if x.bikes < avg - 1]
                    if deficit_stations:
                        target = random.choice(deficit_stations)
                        s.bikes -= 1
                        target.bikes += 1
