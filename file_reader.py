

class gcode_file:

    def __init__(self,path):
        self.content=None
        self.state=None
        try:
            with open('path','r')as f:
                self.content=f.readlines()
                self.state=True
        except:
            self.state=False
    


