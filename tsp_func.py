import math
import random
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib import animation
from copy import deepcopy

# read tool va arze joghrafia
def parse_latlng(fname):
    data = pd.read_csv(fname)
    lat, lng = data['lat'].values, data['lng'].values
    return list([Point2D(x, y) for x, y in zip(lng, lat)])

# plot history for SA
def plot_sa_history(history):
    plt.figure(figsize=(8, 4))
    plt.plot([tour.len for tour in history])
    plt.xlabel('Iteration')
    plt.ylabel('Tour length')
    plt.show()
    
# plot fitness GA 
def plot_fitness(bests, means=None):
    plt.figure(figsize=(8, 4))
    if means:
        plt.plot(means, label='Average')
    plt.plot(bests, label='Best')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.legend(loc='best')
    plt.show()
    

  # plot  iran  map
class Point2D:
    
    def __init__(self, x=None, y=None, width=999, height=666):
        if x is None:
            self.x = random.randint(1, width)
            self.y = random.randint(1, height)
        else:
            self.x, self.y = x, y
            
    def distance(self, other, x_scale=94.05163, y_scale=110.89431):
        dx = (self.x - other.x) * x_scale
        dy = (self.y - other.y) * y_scale    
        return math.sqrt(dx ** 2 + dy ** 2)
    
    def __str__(self):
        return "({:.2f}, {:.2f})".format(self.x, self.y)
    
    def __repr__(self):
        return str(self)


class Tour:
    def __init__(self, cities):
        self.N = len(cities) #number of city
        self.cities = cities #phenotype
        self.ids = list(range(self.N)) # genotype
        random.shuffle(self.ids)
        self.len = -1
        # cost function
    def length(self):
        if self.len < 0:
            self.len = sum([self.cities[self.ids[i-1]].distance(self.cities[self.ids[i]])
                            for i in range(self.N)])        
            
        return self.len 
    
    def random_neighbor(self):# genarate random neighbor
        neighbor = deepcopy(self)
        
        i = random.randint(0, self.N - 2)
        j = random.randint(i + 1, self.N - 1)
        
        c = random.choice([1, 2, 2, 2]) # posibility 0.25 swap
        if c == 1:
            neighbor.ids[i], neighbor.ids[j] = neighbor.ids[j], neighbor.ids[i]
        elif c == 2: # posibility 0.75 reverse
            neighbor.ids[i: j + 1] = reversed(neighbor.ids[i: j + 1])
        else:
            random.shuffle(neighbor.ids[i: j + 1])
            
        neighbor.len = -1  # neighbor.length()
        return neighbor
    
    def plot(self, style='bo-', show_length=True): #  plot Iran map
        fig = plt.figure(figsize=(6, 6))
        
        m = Basemap(projection='gnom', resolution='l', 
                    lat_0=32.5, lon_0=54,
                    width=1.8E6, height=1.7E6)

        m.drawcoastlines(color='gray')
        m.drawcountries(color='black')
        
        # plot tours
        start = self.ids[0:1]
        xs = [self.cities[i].x for i in self.ids + start]
        ys = [self.cities[i].y for i in self.ids + start]
        m.plot(xs, ys, 'b-', color='darkslateblue', clip_on=False, latlon=True, alpha=0.5)
        m.scatter(xs, ys, latlon=True, c='darkslateblue', s=20)
        if show_length:
            plt.title("Length = {:.2f} (km)".format(self.length()))
        plt.axis('off')
            
    def __str__(self):
        return "{} <{:.2f}>".format(self.ids, self.len)
    
    def __len__(self):
        return self.N
    
    # animation
def create_animation_plot(history, xlim, ylim, step=10, figsize=(6, 6), dpi=150):
    history = history[::step]
    fig = plt.figure(dpi=dpi, figsize=figsize)
    
    m = Basemap(projection='gnom', resolution='l', 
                lat_0=32.5, lon_0=54,
                width=1.8E6, height=1.7E6)

    m.drawcoastlines(color='gray')
    m.drawcountries(color='black')
    
    minx, miny = m(xlim[0] - 0.5, ylim[0] - 0.5)
    maxx, maxy = m(xlim[1] + 3.0, ylim[1] + 0.5)
    plt.xlim(minx, maxx)
    plt.ylim(miny, maxy)    
    plt.axis('off')
    
    line, = m.plot([], [], 'o-', color='darkslateblue', markersize=5, latlon=True)

    # animation function.
    def animate(i):
        tour = history[i]
        start = tour.cities[tour.ids[0]]
        x = [tour.cities[j].x for j in tour.ids] + [start.x]
        y = [tour.cities[j].y for j in tour.ids] + [start.y]
        x, y = m(x, y)
        line.set_data(x, y)
        plt.title("Iteration {}: length = {:.2f}".format(i, tour.len), fontsize=12)
        return line,

    anim = animation.FuncAnimation(fig, animate, frames=len(history),
                                   interval=30, repeat_delay=1000)
    
    anim.save(f'imgs/{history[0].N}-tsp-sa.gif', writer='ffmpeg')
    return anim
