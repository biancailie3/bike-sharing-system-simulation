import simpy
import random
import matplotlib.pyplot as plt

NUM_DAYS = 20
DAY_LENGTH = 720
REBALANCE_INTERVAL = 20
REPAIR_TIME_RANGE = (60, 180)

time_slots = [
    {'name': 'morning', 'start': 0, 'end': 120, 'failure_prob': 0.08},
    {'name': 'midday', 'start': 120, 'end': 480, 'failure_prob': 0.05},
    {'name': 'evening', 'start': 480, 'end': 720, 'failure_prob': 0.03},
]

class BikeStation:
    def __init__(self, name, capacity, init_bikes):
        self.name = name
        self.capacity = capacity
        self.bikes = init_bikes
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

class BikeSharingSystem:
    def __init__(self, env, stations):
        self.env = env
        self.stations = stations
        self.unhappy_no_bike = 0
        self.unhappy_no_space = 0
        self.broken_bikes = 0
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
        travel_time = random.randint(5, 30)
        yield self.env.timeout(travel_time)
        current_time_in_day = self.env.now % DAY_LENGTH
        for slot in time_slots:
            if slot['start'] <= current_time_in_day < slot['end']:
                current_failure_prob = slot['failure_prob']
                break
        if random.random() < current_failure_prob:
            self.broken_bikes += 1
            repair_time = random.randint(*REPAIR_TIME_RANGE)
            yield self.env.timeout(repair_time)
            self.broken_bikes -= 1
        else:
            if not end_station.return_bike():
                self.unhappy_no_space += 1

    def rebalancer(self):
        while True:
            yield self.env.timeout(REBALANCE_INTERVAL)
            avg_bikes = sum(s.bikes for s in self.stations) / len(self.stations)
            for s in self.stations:
             while s.bikes > avg_bikes + 1:
                deficit_stations = [x for x in self.stations if x.bikes < avg_bikes - 1]
                if deficit_stations:
                     target = random.choice(deficit_stations)
                     s.bikes -= 1
                     target.bikes += 1
                else:
                  break

    def record_data(self):
        for s in self.stations:
            s.level_history.append(s.bikes)

env = simpy.Environment()

stations = [
    BikeStation("A", capacity=10, init_bikes=6),
    BikeStation("B", capacity=12, init_bikes=8),
    BikeStation("C", capacity=8, init_bikes=5),
    BikeStation("D", capacity=15, init_bikes=10),
]


system = BikeSharingSystem(env, stations)

def data_collector(env, system):
    while True:
        yield env.timeout(10)
        system.record_data()

env.process(data_collector(env, system))
env.run(until=NUM_DAYS * DAY_LENGTH)

for s in stations:
    plt.plot(s.level_history, label=f"Station {s.name}")

plt.legend()
plt.title("Bike Levels Over Time")
plt.xlabel("Timp (x10 minute)")
plt.ylabel("Număr biciclete")
plt.show()

print("\nRezumat:")
print(f"Clienți nefericiți (fără bicicletă): {system.unhappy_no_bike}")
print(f"Clienți nefericiți (stații pline): {system.unhappy_no_space}")
print(f"Biciclete în reparație (final): {system.broken_bikes}")
