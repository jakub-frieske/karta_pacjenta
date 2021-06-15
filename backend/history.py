
class history:
    def __init__(self,id,date,before,valueb):
        self.id = id
        self.date =date
        self.before = before
        self.value = valueb
        self.toString = f"{date}\t {before}"