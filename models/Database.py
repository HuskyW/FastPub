
class Database():
    def __init__(self):
        pass


    def query(self,query):
        pass


class CountingDatabase(Database):
    def __init__(self,l_max,k,population_size):
        self.data = {}
        self.l_max = l_max
        self.k = k
        self.population_size = population_size

    def add_record(self,fragment,count):
        if fragment not in self.data.keys():
            self.data[fragment] = 0
        self.data[fragment] += count

    def query(self,query):
        if query in self.data.keys():
            return self.data[query]
        qlen = len(query)

        if qlen <= 1:
            return self.k # let TrieHH cheat! FASTPub never use this line
        
        qlist = list(query)
        leftpart = tuple(qlist[0:qlen-1])
        rightpart = tuple(qlist[1:qlen])
        if qlen == 2:
            return self.query(leftpart) * self.query(rightpart) / self.population_size

        middlepart = tuple(qlist[1:qlen-1])

        return self.query(leftpart) * self.query(rightpart) / self.query(middlepart)

    def spell(self):
        for key, val in self.data.items():
            print(key)
            print(val)

class SketchDatabase(Database):
    def __init__(self,handler):
        self.handler = handler

    def query(self,query):
        return self.handler.query(query)
