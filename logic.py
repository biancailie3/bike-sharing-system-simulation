import simpy
import random
import math

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
        
        # Statistici și Contoare
        self.happy_customers = 0    
        self.unhappy_no_bike = 0    
        self.unhappy_no_space = 0   
        
        # Unde sunt bicicletele care nu sunt în stații?
        self.bikes_riding = 0      # Oameni care pedalează acum
        self.bikes_in_truck = 0    # Biciclete aflate în camion
        
        self.env.process(self.customer_generator())
        self.env.process(self.rebalancer())

    def get_distance(self, s1, s2):
        return math.sqrt((s1.lat - s2.lat)**2 + (s1.lon - s2.lon)**2)

    def get_nearest_station(self, current_station):
        others = [s for s in self.stations if s != current_station]
        return min(others, key=lambda s: self.get_distance(current_station, s))

    def customer_generator(self):
        while True:
            # Vin clienți
            yield self.env.timeout(random.expovariate(1/4)) 
            self.env.process(self.handle_customer())

    def handle_customer(self):
        start_station = random.choice(self.stations)
        end_station = random.choice([s for s in self.stations if s != start_station])

        # 1. Încearcă să închirieze
        if not start_station.rent_bike():
            self.unhappy_no_bike += 1
            return 

        # Clientul a luat bicicleta -> E pe traseu
        self.bikes_riding += 1
        
        # 2. Călătoria
        yield self.env.timeout(random.randint(10, 25))

        # 3. Încearcă să returneze
        if end_station.return_bike():
            self.happy_customers += 1
            self.bikes_riding -= 1 # S-a terminat cursa
        else:
            self.unhappy_no_space += 1
            
            # Rerutare către cea mai apropiată
            nearest = self.get_nearest_station(end_station)
            yield self.env.timeout(random.randint(5, 10))
            
            if nearest.return_bike():
                pass 
            else:
                # Dacă și aia e plină, forțăm parcarea (nu lăsăm bicicleta pe stradă)
                # O punem în stație chiar dacă depășește capacitatea (simulare de "lăsată lângă")
                nearest.bikes += 1 
            
            self.bikes_riding -= 1 # S-a terminat cursa (chiar dacă forțat)

    def rebalancer(self):
        truck_capacity = 15
        
        while True:
            yield self.env.timeout(self.rebalance_interval)
            
            total_bikes_stations = sum(s.bikes for s in self.stations)
            # Calculăm media luând în considerare doar ce e în stații
            if len(self.stations) > 0:
                avg = total_bikes_stations // len(self.stations)
            else:
                avg = 0
            
            # PASUL 1: Colectarea (din stații în camion)
            for s in self.stations:
                while s.bikes > avg and self.bikes_in_truck < truck_capacity:
                    s.bikes -= 1
                    self.bikes_in_truck += 1 # Mutăm în camion
            
            # PASUL 2: Distribuția (din camion în stații)
            if self.bikes_in_truck > 0:
                deficit_stations = [s for s in self.stations if s.bikes < avg]
                
                while self.bikes_in_truck > 0 and deficit_stations:
                    target = min(deficit_stations, key=lambda s: s.bikes)
                    target.bikes += 1
                    self.bikes_in_truck -= 1 # Scoatem din camion
                    
                    if target.bikes >= avg:
                        deficit_stations.remove(target)
