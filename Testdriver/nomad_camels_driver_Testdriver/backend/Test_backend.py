class virtualdevice:

    def __init__(self,Resistance):
        self.U = 0
        self.R = Resistance

    
    def set_U(self,U):
        self.U = U

    def get_U(self):
        return self.U

    def get_I(self):
        return self.U / self.R
    
    def cool(self):
        print("device cooled!")

