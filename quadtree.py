class Point:
    def __init__(self, x, y, ref):
        self.x = x
        self.y = y
        self.ref = ref

class QuadTree:
    def __init__(self, x1, x2, y1, y2):
        self.cap = 10
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.points = []
        self.split = False
        self.branches = []

    def insert(self, p):
        if p.x < self.x1:
            return False
        if p.x >= self.x2:
            return False
        if p.y < self.y1:
            return False
        if p.y >= self.y2:
            return False
        
        if len(self.points) < self.cap:
            self.points.append(p)
            return True
        
        if not self.split:
            self.split = True

            self.branches = [
                QuadTree(self.x1, self.x2//2, self.y1, self.y2//2), # TopLeft
                QuadTree(self.x2//2, self.x2, self.y1, self.y2//2), # TopRight
                QuadTree(self.x1, self.x2//2, self.y2//2, self.y2), # BottomLeft
                QuadTree(self.x2//2, self.x2, self.y2//2, self.y2), # BottomRight
            ]
        
        for i in range(4):
            if self.branches[i].insert(p):
                return True
    
    def query(self, x1, x2, y1, y2):
        if x1 >= self.x2:
            return []
        if x2 < self.x1:
            return []
        if y1 >= self.y2:
            return []
        if y2 < self.y1:
            return []
        
        response = self.getPoints(x1, x2, y1, y2)

        if not self.split:
            return response
        
        for i in range(4):
            response.extend(self.branches[i].query(x1, x2, y1, y2))

        return response

    def getPoints(self, x1, x2, y1, y2):
        response = []
        for i in range(len(self.points)):
            if self.points[i].x < x1:
                continue
            if self.points[i].x >= x2:
                continue
            if self.points[i].y < y1:
                continue
            if self.points[i].y >= y2:
                continue

            response.append(self.points[i])
        return response