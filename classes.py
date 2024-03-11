class casesFile:
    new = ""
    accumulated = ""
    population = ""
    sheet_name = ""
    error = False
    
    def __init__(self):
        self.new = ""
        self.accumulated = ""
        self.population = ""
        self.sheet_name = "Cases"        
        self.error = False
    
    def set_new(self, new):
        self.new = new
        
    def set_accumulated(self, accumulated):
        self.accumulated = accumulated
    
    def set_population(self, population):
        self.population = population
    
    def set_sheet_name(self, sheet_name):
        self.sheet_name = sheet_name
        
    def set_error(self, error):
        self.error = error 
        