class playerData:
    def __init__(self,name,potion,HS):
        self.name = name
        self.potion = potion
        self.HS = HS

    def printplayer(self):
        return "name = " + self.name + ", potions=" + str(self.potion) + " ,HS=" + str(self.HS)