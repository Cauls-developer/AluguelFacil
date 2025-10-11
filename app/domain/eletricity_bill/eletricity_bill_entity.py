class eletricity_bill:
    def __init__(self, ri, rf, gc, tc):
        self.readingInital = ri
        self.readingFinal = rf
        self.genralConsumption = gc
        self.totalCost = tc
        self.personalConsumption = self.readingFinal - self.readingInital
        self.personalproportionalConsumption = (self.personalConsumption / self.genralConsumption) * 100
        self.personalcost = (self.personalproportionalConsumption * self.totalCost) / 100

