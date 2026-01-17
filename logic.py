import simpy
import random

# Parametri impliciți
DAY_LENGTH = 720 # 12 ore

class BikeStation:
    def __init__(self, name, capacity, init_bikes, lat, lon):
        self.name = name
        self.capacity = capacity
        self.bikes = init_bikes
        self.lat = lat  
        self.lon = lon 
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
        self.happy_customers = 0
        self.unhappy_no_bike = 0
        self.unhappy_no_space = 0

        self.env.process(self.customer_generator())
        self.env.process(self.rebalancer())

    def customer_generator(self):
        while True:
            yield self.env.timeout(random.expovariate(1/5))
            self.env.process(self.handle_customer())

    def handle_customer(self):
        start_station = random.choice(self.stations)
        end_station = random.choice([s for s in self.stations if s != start_station])

        if not start_station.rent_bike():
            self.unhappy_no_bike += 1
            return

        # Client fericit
        self.happy_customers += 1 
        
        yield self.env.timeout(random.randint(10, 30))

        if not end_station.return_bike():
            self.unhappy_no_space += 1

    def rebalancer(self):
        while True:
            yield self.env.timeout(self.rebalance_interval)
            
            avg = sum(s.bikes for s in self.stations) / len(self.stations)
            truck_capacity = 10  
            bikes_in_truck = 0
            
            # PASUL 1: Colectarea 
            for s in self.stations:
                while s.bikes > avg + 1 and bikes_in_truck < truck_capacity:
                    s.bikes -= 1
                    bikes_in_truck += 1
            
            # PASUL 2: Distribuția
            if bikes_in_truck > 0:
                deficit_stations = [s for s in self.stations if s.bikes < avg - 1]
                
                while bikes_in_truck > 0 and deficit_stations:
                    target = min(deficit_stations, key=lambda s: s.bikes)
                    target.bikes += 1
                    bikes_in_truck -= 1
                    
                    if target.bikes >= avg:
                        deficit_stations.remove(target)
