from random import randrange
import interface as view
import consts
import math

ANTS = []
ANTR = 2
ANTCOST =  1
VIEWCONE = 30
ENDURANCE = 400
HEALTH = 200
POWER = 200
SPEED = 1/3
countx = [0] * 5
county = [0] * 5
CARRYCAPACITY = 10

def search_id(ID,liste):
    """ a changer de place """
    for k in range(len(liste)):
        if ID == liste[k].id:
            return liste[k]

class SimulationObject(object):
    """
    Classe englobant tout les objets de simulation sauf la fourmi
    """

    attributs = {'position', 'id'}
    def __init__(self, pos=-1, objid=-1):
        """
        Permet d'initialiser un objet de simulation

        Parameters
        ----------
        pos : tuple (x1,y1,x2,y2) 
            represente la position de l'objet dans le canvas
        
        objid : int 
            represente l'id de l'objet dans le canvas

        Returns
        -------
        None.

        """
        self.position = pos
        self.id = objid

    def get_parameter(self, p):
        """
        Permet de recuperer le parametre p d'un SimulationObject

        Parameters
        ----------
        p : Paramètre quelconque

        Raises
        ------
        AttributeError
            Si p n'appartient pas au dictionnaire de paramètre

        Returns
        -------
        Retourne la valeur du parametre p d'un certain objet self

        """
        if p in self.attributs:
            return self.__dict__[p]
        else:
            raise AttributeError

    def set_parameter(self, **kwargs):
        """
        Permet d'associer une valeur à un ou plusieurs paramètres

        Parameters
        ----------
        **kwargs : represente tout les arguments possible de l'objet

        Raises
        ------
        AttributeError
            Si le parametre n'appartient pas au dictionnaire de paramètre

        Returns
        -------
        None.

        """
        for param in kwargs:
            if param in self.attributs:
                self.__dict__[param] = kwargs[param]
            else:
                raise AttributeError


class Resource(SimulationObject):
    """
    Classe representant une ressource de la simulation
    """
    attributs = SimulationObject.attributs.union({'quantity'})
    def __init__(self, pos=-1, objid=-1, qty=-1):
        """
        Permet d'initialiser une rsesource dans le canvas

        Parameters
        ----------
        pos : tuple (x1,y1,x2,y2) 
            represente la position de l'objet dans le canvas
        
        objid : int 
            represente l'id de l'objet dans le canvas
            
        qty : int
            represente la quantité de ressource presente dans la ressource

        Returns
        -------
        None.

        """
        SimulationObject.__init__(self, pos, objid)
        self.quantity = qty

    def reduce(self, n):
        """
        Permet de réduire la ressource de n quantité

        Parameters
        ----------
        n : int
            nombre de ressources à enlever de la ressource

        Returns
        -------
        None.

        """
        self.quantity -= n


class Obstacle(SimulationObject):
    """
    Classe representant tout les obstacles possibles
    """

class DiggableWall(Obstacle):
    """
    Classe representant les murs creusables
    """
    attributs = Obstacle.attributs.union({'length'})
    def __init__(self, pos=-1, objid=-1, lgth=-1):
        """
        Permet d'initialiser un mur creusable dans le canvas

        Parameters
        ----------
        pos : tuple (x1,y1,x2,y2) 
            represente la position de l'objet dans le canvas
        
        objid : int 
            represente l'id de l'objet dans le canvas
            
        lgth : int
            represente l'epaisseur (restante) du mur

        Returns
        -------
        None.

        """
        Obstacle.__init__(self, pos, objid)
        self.length = lgth

    def dig(self, n):
        """
        Permet de réduire l'epaisseur du mur

        Parameters
        ----------
        n : int
            represente la taille de la réduction

        Returns
        -------
        None.

        """
        self.length -= n


class Water(Obstacle):
    """
    Classe representant l'eau dans la simulation
    """
    attributs = Obstacle.attributs.union({'bridge_width', 'number_of_ants',
                                          'ants'})
    def __init__(self, pos=-1, objid=-1, brwdth=-1):
        """
        

        Parameters
        ----------
        pos : tuple (x1,y1,x2,y2) 
            represente la position de l'objet dans le canvas
        
        objid : int 
            represente l'id de l'objet dans le canvas
            
        brwdth : int
            represente l'epaisseur du pont si il existe.
            vaut -1 si il n'y en a pas.

        Returns
        -------
        None.

        """
        Obstacle.__init__(self, pos, objid)
        self.bridge_width = brwdth
        self.number_of_ants = 0
        self.ants = []

    def add_to_bridge(self, n, *ants):
        """
        Permet d'ajouter des fourmis au pont

        Parameters
        ----------
        n : int
            représente le nombre de fourmi s'ajoutant au pont
        *ants : class *ant 
            représente toutes les fourmis s'ajoutant sur le pont

        Returns
        -------
        None.

        """
        self.number_of_ants += n
        for ant in ants:
            self.ants += [ant]


class SpacePortal(SimulationObject):
    """
    Classe représentant une paire de portails spatiaux dans la simulation
    """
    attributs = SimulationObject.attributs.union({'capacity', 'other_portal'
                                                  'loading_time'})
    def __init__(self, pos=-1, objid=-1, cap=-1, loading=-1, otherP=-1):
        """
        Permet d'initialiser la paire de portails dans le canvas

        Parameters
        ----------
        pos : tuple (x1,y1,x2,y2) 
            represente la position de l'objet dans le canvas
        
        objid : int 
            represente l'id de l'objet dans le canvas
            
        cap : int
            représente le nombre d'utilisation du portail
            
        loading : int
            représente le temps de chargement du portail
            
        otherP : SpacePortal
            represente le portail dual d'un portail

        Returns
        -------
        None.

        """
        SimulationObject.__init__(self, pos, objid)
        self.capacity = cap
        self.loading_time = loading
        self.other_portal = otherP

    def switch(self, A):
        """
        Permet d'échanger de place une fourmi traversant un portail

        Parameters
        ----------
        A : Ant
            Represente une fourmi dans un portail

        Returns
        -------
        None.

        """
        x1, y1, x2, y2 = self.other_portal.position
        xc = (x1 + x2) / 2
        yc = (y1 + y2) / 2
        r = abs(x2 - x1) / 1 + ANTR 
        angle = math.radians((A.field_of_view*22.5)) + math.pi
        xn = xc + r*math.cos(angle)
        yn = yc + r* math.sin(angle)
        A.position = [xn,yn]
        consts.canv.coords(A.id, xn + ANTR , yn + ANTR, xn - ANTR , yn - ANTR)


class Pathogen(SimulationObject):
    """
    Represente un pathogene present dans la simulation
    """
    attributs = SimulationObject.attributs.union({'infection_rate',
                                                  'incubation_time',
                                                  'kill_rate',
                                                  'infection_radius',
                                                  'quantity'})
    def __init__(self, pos=-1, objid=-1, infrat=-1, incut=-1, killra=-1,
                 infrad=-1, qty=-1):
        """
        Permet d'initialiser un pathogene dans le canvas

        Parameters
        ----------
        pos : tuple (x1,y1,x2,y2) 
            represente la position de l'objet dans le canvas
        
        objid : int 
            represente l'id de l'objet dans le canvas
            
        infrat : int
            Represente le poucentage qu'une fourmi infecte une autre fourmi 
            
        incut : int
            Represente le temps d'incubation de la maladie sur une fourmi
            
        killra : int
            Represente le pourcentage qu'une fourmi meurs apres sa periode
            d'incubation
        
        infrad : float
            Represente le rayon pour qu'une fourmi infectée puisse contaminer
            d'autres fourmis
            
        qty : int
            Represente le nombre de pathogene present. 

        Returns
        -------
        None.

        """
        SimulationObject.__init__(self, pos, objid)
        self.infection_rate = infrat
        self.incubation_time = incut
        self.kill_rate = killra
        self.infection_radius = infrad
        self.quantity = qty

    def infect_ant(self, A):
        """
        Permet de tranferer les caractéristiques d'infection a la fourmi

        Parameters
        ----------
        A : Ant
            Represente une fourmi venant d'être infectée

        Returns
        -------
        None.

        """
        A.infected = True
        A.incubation_time = self.incubation_time
        A.pathogen = self
        consts.canv.itemconfigure(A.id, fill="black",width="5")


class Nest(SimulationObject):
    """
    Classe representant un nid dans la simulation
    """

    attributs = SimulationObject.attributs.union({'faction', 'resources',
                                                  'spawn_number',
                                                  'soldier_rate', 'canv',
                                                  'ant_population'})

    def __init__(self, pos=-1, objid=-1, fac=-1, res=-1, spawn=-1, solra=-1):
        """
        Permet d'initialiser un nid dans le canvas

        Parameters
        ----------
        pos : tuple (x1,y1,x2,y2) 
            Represente la position de l'objet dans le canvas
        
        objid : int 
            Represente l'id de l'objet dans le canvas
            
        fac : string
            Represente la faction auquelle le nid et ses fourmis appartienenent
            Faction est représenté par une couleur
            
        res : int
            Represente le nombre de ressources dans le nid
            
        spawn : int
            Represente le nombre de fourmis pouvant apparaître à la fois.
            
        solra : int
            Represente le pourcentage qu'une fourmi soldat apparaisse
            -1 veut dire que le nid ne peut creer de fourmis soldats.

        Returns
        -------
        None.

        """
        SimulationObject.__init__(self, pos, objid)
        self.faction = fac
        self.resources = res
        self.spawn_number = spawn
        self.soldier_rate = solra
        self.ant_population = 0

    def spawn_ants(self):
        """
        Méthode permettant de faire apparaitre les fourmis depuis le nid

        Parameters
        ----------
        
        Returns
        -------
        None.

        """
        global ANTS
        for i in range(self.spawn_number):
            fac = self.faction
            if self.resources < ANTCOST:
                break
            drct = randrange(16)
            xc = self.position[0] + self.position[2]
            yc = self.position[1] + self.position[3]
            xc, yc = xc/2, yc/2
            
            if randrange(100) <= self.soldier_rate:
                antr = ANTR + 1
                P = [xc - antr, yc - antr, xc + antr, yc + antr]
                obj = view.create_ant(P, fac, "soldier")
                newAnt = SoldierAnt(self.faction, [xc, yc], ENDURANCE,
                                    drct, HEALTH, POWER, self, obj)
            else:
                antr = ANTR
                P = [xc - antr, yc - antr, xc + antr, yc + antr]
                obj = view.create_ant(P, fac, "worker")
                newAnt = WorkerAnt(self.faction, [xc, yc], ENDURANCE,
                                   drct, HEALTH, POWER, self, obj)
            self.ant_population += 1
            self.resources -= ANTCOST
            ANTS += [newAnt]
            consts.Dobj[newAnt.id] = newAnt

class Ant(object):
    """
    Cette classe represente une fourmi cree par un nid 
    """

    attributs={'faction', 'position', 'endurance', 'field_of_view', 'health',
               'power' , 'nid_id', 'infected', 'incubation_time'}

    def __init__(self, fac=-1, pos=-1, end=-1, fov=-1, health=-1, power=-1,
                 nid=-1, objid=-1):
        """
        Initialise une fourmi dans la simulation

        Parameters
        ----------
        fac : string
            Represente la faction du nid. Voir nid.
            
        pos : tuple
            Represente la position de la fourmi
            
        end : int
            Represente l'endurance de la fourmi, à 0 elle doit revenir au nid
            
        fov : int
            Represente son cône de vision. Allant de 0 a 15, chaque numéros
            représentent une portion d'angle de 22.5 degrès
            
        health : int
            Represente les points de vie d'une fourmi
            
        power : int
            Represente les points d'attaques d'une fourmi
            
        nid : Nest
            Représente le nid-mère de la fourmi
            
        objid : int
            Réprésente l'id de l'objet dans le canvas

        Returns
        -------
        None.

        """
        self.faction = fac
        self.position = pos
        self.id = objid
        self.endurance = end
        self.field_of_view = fov
        self.infected = False
        self.incubation_time = -1
        self.pathogen = -1
        self.health = health
        self.power = power
        self.nid_id = nid

    def attack(self, enemy):
        """
        Permet l'attaque d'une fourmi sur une autre

        Parameters
        ----------
        enemy : Ant
            Fourmi adverse

        Returns
        -------
        None.

        """
        enemy.health -= self.power
        self.endurance -= n

    def get_infected(self, t):
        """
        Represente l'infection de la fourmi par le pathogene t'

        Parameters
        ----------
        t : Pathogen
            Pathogène infectant la fourmi

        Returns
        -------
        None.

        """
        t.infect_ant(self)
        tags = consts.canv.gettags(self.id)
        tags = tags + ("infected",)
        consts.canv.itemconfigure(self.id, tags=tags)
        
    def move(self):
        """
        Méthode du déplacement de la fourmi

        Returns
        -------
        None.

        """
        
        
        x, y = round(self.position[0]), round(self.position[1])
        offset = 13
        canvw = consts.canvw - offset
        canvh = consts.canvh - offset
        if self.infected == True:
            if self.incubation_time != 0:
                self.incubation_time += -1
            else:
                rate = self.pathogen.kill_rate
                roll = randrange(100)
                if roll <= rate:
                    consts.canv.delete(self.id)
                    ANTS.remove(self)
                    pass
            r = self.pathogen.infection_radius
            P = consts.canv.find_overlapping(x - r, y - r, x + r, y + r)
            T = []
            for j in range(len(P)):
                if "ant" in consts.canv.gettags(P[j]):
                    T += [search_id(P[j], ANTS)]
            rate = self.pathogen.infection_rate
            for ant in T:
                if ant.infected == False:
                    roll = randrange(100)
                    if roll <= rate :
                        ant.get_infected(self.pathogen)

                        
                        
        
        
        maxroll = 100
        a = randrange(maxroll + 1)
        a = (0 < a) + (a == maxroll)
        fov = self.field_of_view

        #########
        # 12345 #
        # 0   6 #
        # F X 7 #
        # E   8 #
        # DCBA9 #
        ######### 

        NIDR = consts.NESTR
        U = self.nid_id.position
        x1 = self.position[0]
        y1 = self.position[1]
        nid_center = ((U[0] + U[2]) / 2),((U[1] + U[3]) / 2)
        if self.endurance <= 0:
            if nid_center[0] - NIDR < x < nid_center[0] + NIDR and\
                    nid_center[1] - NIDR < y1 < nid_center[1] + NIDR:
                fov = (fov + 8) % 16 
                self.endurance = ENDURANCE
                        
        
        fov = ((fov) - 1) % 16
        DX = [(3 < fov < 11) + (4 < fov < 10) - (fov < 3) - (fov > 11)\
              - (fov < 2) - (fov > 12),
              (3 < ((fov + 1) % 16) < 11) + (4 < ((fov + 1) % 16) < 10)\
              - (((fov + 1) % 16) < 3) - (((fov + 1) % 16) > 11)\
              - (((fov + 1) % 16) < 2) - (((fov + 1) % 16) > 12),
              (3 < ((fov + 2) % 16) < 11) + (4 < ((fov + 2) % 16) < 10)\
              - (((fov + 2) % 16) < 3) - (((fov + 2) % 16) > 11)\
              - (((fov + 2) % 16) < 2) - (((fov + 2) % 16) > 12)]
        
        
        DY = [(7 < fov < 15) + (8 < fov < 14) - (fov < 7) - (0 < fov < 6),
              (7 < ((fov + 1) % 16) < 15) + (8 < ((fov + 1) % 16) < 14)\
              - (((fov + 1) % 16) < 7) - (0 < ((fov + 1) % 16) < 6),
              (7 < ((fov + 2) % 16) < 15) + (8 < ((fov + 2) % 16) < 14)\
              - (((fov + 2) % 16) < 7) - (0 < ((fov + 2) % 16) < 6)]
        
        
        case1 = int(consts.mat[(x + DX[0]) % canvw][(y + DY[0]) % canvh])
        case2 = int(consts.mat[(x + DX[1]) % canvw][(y + DY[1]) % canvh])
        case3 = int(consts.mat[(x + DX[2]) % canvw][(y + DY[2]) % canvh])
        case1 += 1000 * (case1 == 0)
        case1 *= (case1 > -1)
        case2 += 1000 * (case2 == 0)
        case2 *= (case2 > -1)
        case3 += 1000 * (case3 == 0)
        case3 *= (case3 > -1)
        phstack = case1 + case2 + case3
        phstack = int(phstack)
        phstack *= phstack > 1
        
        if phstack != 0:
            c = randrange(200)
            c = c != 0
            d = randrange(phstack + (phstack == 0))
            temp = phstack - consts.mat[(x + DX[2]) % canvw][(y + DY[2]) % canvh]
            temp = int(temp)
            temp2 = consts.mat[(x + DX[0]) % canvw][(y + DY[0]) % canvh]
            temp2 = int(temp2)
            d = int(d >= temp) + int(d >= temp2)
            dx = DX[a * (c == 0) + d * c]
            dy = DY[a * (c == 0) + d * c]
            newx = x + dx * consts.speedmod.get()
            newy = y + dy * consts.speedmod.get()
            newx, newy = round(newx) % canvw, round(newy) % canvh
            if consts.mat[newx][newy] <= -1 and consts.mat[newy][newx] > -1:
                dx, dy = dy, dx
                fov = (fov - 4) % 16
            elif consts.mat[newx][newy] <= -1 and consts.mat[newy][newx] <= -1:
                dx, dy = -dx, -dy
                fov = (fov + 8) % 16
            else:
                fov = (fov + a * c + d * (c == 0)) % 16
        else:
            dx = DY[1]
            dy = DX[1]
            fov = (fov - 4) % 16
        dx *= consts.speedmod.get()
        dy *= consts.speedmod.get()
        consts.canv.move(self.id, dx, dy)
        self.position[1] += dy
        self.position[0] += dx
        
        # retour au nid
        qsd = randrange(round(20 / consts.speedmod.get()))
        if self.endurance <= 0 and (not qsd):
            x2, y2 = x1 - nid_center[0], y1 - nid_center[1]
            theta = (math.atan2(y2, x2) + 2 * math.pi)
            theta = (math.degrees(theta) % 360)
            fov = int(theta / (360 / 16))
        
        # out of bounds
        LR = [6, 5, 4, 11, 2, 1, 0, 15, 14, 13, 12, 3, 10, 9, 8, 7]
        UD = [14, 13, 12, 11, 10, 9, 8, 15, 6, 5, 4, 3, 2, 1, 0, 7]
        dlr = (fov == 0) or (fov > 13) or (5 < fov < 9)
        dud = (1 < fov < 5) or (9 < fov < 13)
        dcr = (fov == 1) or (fov == 5) or (fov == 9) or (fov == 13)
        ooblr = not (offset <= self.position[0] < canvw)
        oobud = not (offset <= self.position[1] < canvh)
        noob = not (ooblr or oobud) #and (phstack != 0)
        coob = (ooblr and oobud)# or (phstack == 0)
        if not noob:
            if self.position[0] < offset:
                self.position[0] = offset
            elif self.position[0] >= canvw:
                self.position[0] = canvw - 1
            if self.position[1] < offset:
                self.position[1] = offset
            elif self.position[1] >= canvh:
                self.position[1] = canvh - 1
        self.field_of_view = fov * noob +  LR[fov] * ooblr + UD[fov] * oobud
        self.field_of_view *= (1 - coob)
        self.field_of_view += (fov + 8) * coob
        self.endurance -= consts.speedmod.get()

        
        
        # case d'arrivée pathogen ?

        x, y = (self.position[0]), (self.position[1])
        if self.infected == False:
            r = 10 #infection radius "global" arbitraire
            P = consts.canv.find_overlapping(x - r, y - r, x + r, y + r)
            t = len(P)+1
            for j in range(len(P)):
                if ("pathogen" in consts.canv.gettags(P[j])):
                    t = j
            if t < len(P):
                patho = consts.Dobj[P[t]]
                self.get_infected(patho)
                patho.quantity += -1
                if patho.quantity == 0:
                    consts.canv.delete(patho.id)
                    consts.Dobj.pop(patho.id)
        # case d'arrivée portail ?
        Port = consts.canv.find_overlapping(x - ANTR, y - ANTR, x + ANTR, y + ANTR)
        
        t = len(Port)+1
        for j in range(len(Port)):
            
            if ("portal" in consts.canv.gettags(Port[j])):
                t = j
        if t < len(Port):
            portal = consts.Dobj[Port[t]]
            portal.switch(self)
            portal.capacity += -1
            portal.other_portal.capacity += -1
            if portal.capacity == 0:
                consts.canv.delete(portal.id)
                consts.canv.delete(portal.other_portal.id)
                consts.Dobj.pop(portal.id)
                consts.Dobj.pop(portal.other_portal.id)
                    
            


    def pheromone(self, t):
        """
        méthode du depot de phéromone

        Parameters
        ----------
        t : string
            represente le type de phéromone déposée

        Returns
        -------
        None.

        """
        fov = self.field_of_view
        x, y = round(self.position[0]), round(self.position[1])
        fx = (3 < fov < 11) + (4 < fov < 10) - (fov < 3) - (fov > 11)\
              - (fov < 2) - (fov > 12)
        fy = (7 < fov < 15) + (8 < fov < 14) - (fov < 7) - (0 < fov < 6)
        spd = int(consts.speedmod.get())
        for i in range(-spd - 1, spd + 2):
            xi = x + fx * i
            yi = y + fy * i
            if consts.mat[xi % consts.canvw][yi % consts.canvh] >= 1:
                consts.mat[xi % consts.canvw][yi % consts.canvh] += 100
        


class SoldierAnt(Ant):
    """ 
    Cette classe represente une fourmi guerriere
    """
    def guard(self):
        """
         Méthode permettant à la fourmi guerrière de patrouiller

        Returns
        -------
        None.

        """
        pass

class WorkerAnt(Ant):
    """
    Cette classe represente une fourmi travailleuse
    """
    attributs = Ant.attributs.union({'resources'})
    def __init__(self, fac=-1, pos=-1, end=-1, fov=-1, health=-1, power=-1,
                 nid=-1, objid=-1, res=0):
        """
        

        Parameters
        ----------
        fac : string
            Represente la faction du nid. Voir nid.
            
        pos : tuple
            Represente la position de la fourmi
            
        end : int
            Represente l'endurance de la fourmi, à 0 elle doit revenir au nid
            
        fov : int
            Represente son cône de vision. Allant de 0 a 15, chaque numéros
            représentent une portion d'angle de 22.5 degrès
            
        health : int
            Represente les points de vie d'une fourmi
            
        power : int
            Represente les points d'attaques d'une fourmi
            
        nid : Nest
            Représente le nid-mère de la fourmi
            
        objid : int
            Réprésente l'id de l'objet dans le canvas
            
        res : int
            Représente la quantité de ressources que porte la fourmi

        Returns
        -------
        None.

        """
        Ant.__init__(self, fac, pos, end, fov, health, power, nid, objid)
        self.resources = res

    def collect(self, R):
        """
        Méthode representant la collecte de la resource R
        par la fourmi travailleuse

        Parameters
        ----------
        R : Resource
            Resource se faisant collecter

        Returns
        -------
        None.

        """
        if (CARRYCAPACITY - self. resources) <= R.quantity:
            amount = CARRYCAPACITY - self.resources
        else:
            amount = R.quantity
        R.reduce(amount)
        self.resources += amount

    def create_bridge(self, W):
        """
        Méthode permettant de créer un pont sur l'eau W

        Parameters
        ----------
        W : Water
            Eau dans laquelle la fourmi va creer un pont

        Returns
        -------
        None.

        """
        W.add_to_bridge(1,self)

    def dig(self, D):
        """
        Méthode permettant de creuser dans le mur creusable D

        Parameters
        ----------
        D : Digable_Wall
            Mur creusable dans lequel la fourmi creuse

        Returns
        -------
        None.

        """
        D.dig(consts.speedmod.get())

    def move(self):
        global ANTS
        """
        Méthode du déplacement de la fourmi, redéfinie pour worker.

        Returns
        -------
        None.

        """
        
        
        x, y = round(self.position[0]), round(self.position[1])
        offset = 13
        canvw = consts.canvw - offset
        canvh = consts.canvh - offset
        if self.infected == True:
            if self.incubation_time != 0:
                self.incubation_time += -consts.speedmod.get()
            else:
                rate = self.pathogen.kill_rate
                roll = randrange(100)
                if roll <= rate:
                    consts.canv.delete(self.id)
                    ANTS.remove(self)
                    pass
            r = self.pathogen.infection_radius
            P = consts.canv.find_overlapping(x - r, y - r, x + r, y + r)
            T = []
            for j in range(len(P)):
                if "ant" in consts.canv.gettags(P[j]):
                    T += [search_id(P[j], ANTS)]
            rate = self.pathogen.infection_rate
            for ant in T:
                if ant.infected == False:
                    roll = randrange(100)
                    if roll <= rate :
                        ant.get_infected(self.pathogen)

                        
                        
        
        
        maxroll = 100
        a = randrange(maxroll + 1)
        a = (0 < a) + (a == maxroll)
        fov = self.field_of_view

        #########
        # 12345 #
        # 0   6 #
        # F X 7 #
        # E   8 #
        # DCBA9 #
        ######### 

        NIDR = consts.NESTR
        U = self.nid_id.position
        x1 = self.position[0]
        y1 = self.position[1]
        nid_center = ((U[0] + U[2]) / 2),((U[1] + U[3]) / 2)
        if self.resources > 0 or self.endurance <= 0:
            if nid_center[0] - NIDR < x < nid_center[0] + NIDR and\
                    nid_center[1] - NIDR < y1 < nid_center[1] + NIDR:
                self.nid_id.resources += self.resources
                self.resources = 0
                fov = (fov + 8) % 16 
                self.endurance = ENDURANCE
            #elif not ((U[0] < x < U[2]) and (U[1] < y < U[3])):
            else:
                if self.resources > 0:
                    self.pheromone(None)
            
        if consts.mat[x % canvw][y % canvh] == 0:
            res = None
            oblist = consts.canv.find_overlapping(x - 1, y - 1, x + 1, y + 1)
            for obj in oblist:
                tags = consts.canv.gettags(obj)
                if "resource" in tags:
                    res = obj
                    break
            if res:
                ressource = consts.Dobj[res]
                if self.resources < CARRYCAPACITY:
                    self.collect(ressource)
                    fov = (fov + 8 * (self.endurance != 0)) % 16
                if ressource.quantity == 0:
                    xr1, yr1, xr2, yr2 = consts.canv.coords(res)
                    consts.canv.delete(res)
                    rad = xr2 - xr1
                    xr1 = int(xr1)
                    yr1 = int(yr1)
                    rad = int(rad)
                    consts.mat[xr1:xr1 + rad, yr1:yr1 + rad] = 1
    

                    del ressource
                        
        
        fov = ((fov) - 1) % 16
        DX = [(3 < fov < 11) + (4 < fov < 10) - (fov < 3) - (fov > 11)\
              - (fov < 2) - (fov > 12),
              (3 < ((fov + 1) % 16) < 11) + (4 < ((fov + 1) % 16) < 10)\
              - (((fov + 1) % 16) < 3) - (((fov + 1) % 16) > 11)\
              - (((fov + 1) % 16) < 2) - (((fov + 1) % 16) > 12),
              (3 < ((fov + 2) % 16) < 11) + (4 < ((fov + 2) % 16) < 10)\
              - (((fov + 2) % 16) < 3) - (((fov + 2) % 16) > 11)\
              - (((fov + 2) % 16) < 2) - (((fov + 2) % 16) > 12)]
        
        
        DY = [(7 < fov < 15) + (8 < fov < 14) - (fov < 7) - (0 < fov < 6),
              (7 < ((fov + 1) % 16) < 15) + (8 < ((fov + 1) % 16) < 14)\
              - (((fov + 1) % 16) < 7) - (0 < ((fov + 1) % 16) < 6),
              (7 < ((fov + 2) % 16) < 15) + (8 < ((fov + 2) % 16) < 14)\
              - (((fov + 2) % 16) < 7) - (0 < ((fov + 2) % 16) < 6)]
        
        
        case1 = int(consts.mat[(x + DX[0]) % canvw][(y + DY[0]) % canvh])
        case2 = int(consts.mat[(x + DX[1]) % canvw][(y + DY[1]) % canvh])
        case3 = int(consts.mat[(x + DX[2]) % canvw][(y + DY[2]) % canvh])
        case1 += 1000 * (case1 == 0)
        case1 *= (case1 > -1)
        case2 += 1000 * (case2 == 0)
        case2 *= (case2 > -1)
        case3 += 1000 * (case3 == 0)
        case3 *= (case3 > -1)
        phstack = case1 + case2 + case3
        phstack = int(phstack)
        phstack *= phstack > 1
        
        if phstack != 0:
            c = randrange(200)
            c = c != 0
            d = randrange(phstack + (phstack == 0))
            temp = phstack - consts.mat[(x + DX[2]) % canvw][(y + DY[2]) % canvh]
            temp = int(temp)
            temp2 = consts.mat[(x + DX[0]) % canvw][(y + DY[0]) % canvh]
            temp2 = int(temp2)
            d = int(d >= temp) + int(d >= temp2)
            dx = DX[a * (c == 0) + d * c]
            dy = DY[a * (c == 0) + d * c]
            newx = x + dx * consts.speedmod.get()
            newy = y + dy * consts.speedmod.get()
            newx, newy = round(newx) % canvw, round(newy) % canvh
            if consts.mat[newx][newy] <= -1 and consts.mat[newy][newx] > -1:
                dx, dy = dy, dx
                fov = (fov - 4) % 16
            elif consts.mat[newx][newy] <= -1 and consts.mat[newy][newx] <= -1:
                dx, dy = -dx, -dy
                fov = (fov + 8) % 16
            else:
                fov = (fov + a * c + d * (c == 0)) % 16
        else:
            dx = DY[1]
            dy = DX[1]
            fov = (fov - 4) % 16
        dx *= consts.speedmod.get()
        dy *= consts.speedmod.get()
        
        #mur creusable ? eau ?
        Port = consts.canv.find_overlapping(x - ANTR, y - ANTR, x + ANTR, y + ANTR)
        
        t = len(Port) + 1
        w = len(Port) + 1
        for j in range(len(Port)):
            
            if ("diggable" in consts.canv.gettags(Port[j])):
                t = j
            if ("water" in consts.canv.gettags(Port[j])):
                w = j
        if t < len(Port):
            diggable = consts.Dobj[Port[t]]
            if self.resources > 0:
                self.resources -= consts.speedmod.get()
                self.dig(diggable)
                if diggable.length == 0:
                    consts.canv.delete(diggable.id)
                    consts.Dobj.pop(diggable.id)
                dx = 0
                dy = 0
        if w < len(Port):
            water = consts.Dobj[Port[w]]
            if not (self  in water.ants):
                self.create_bridge(water)
                if len(water.ants) == water.bridge_width:
                    for ant in water.ants:
                        consts.canv.delete(ant.id)
                        ANTS.remove(ant)
                    consts.canv.delete(water.id)
                    consts.Dobj.pop(water.id)
            dx = 0
            dy = 0
                
                
        
                
        #move
        consts.canv.move(self.id, dx, dy)
        self.position[1] += dy
        self.position[0] += dx
        
        
        # retour au nid
        qsd = randrange(round(20 / consts.speedmod.get()))
        if (self.resources > 0 or self.endurance <= 0) and (not qsd):
            x2, y2 = x1 - nid_center[0], y1 - nid_center[1]
            theta = (math.atan2(y2, x2) + 2 * math.pi)
            theta = (math.degrees(theta) % 360)
            fov = int(theta / (360 / 16))
        
        # out of bounds
        LR = [6, 5, 4, 11, 2, 1, 0, 15, 14, 13, 12, 3, 10, 9, 8, 7]
        UD = [14, 13, 12, 11, 10, 9, 8, 15, 6, 5, 4, 3, 2, 1, 0, 7]
        dlr = (fov == 0) or (fov > 13) or (5 < fov < 9)
        dud = (1 < fov < 5) or (9 < fov < 13)
        dcr = (fov == 1) or (fov == 5) or (fov == 9) or (fov == 13)
        ooblr = not (offset <= self.position[0] < canvw)
        oobud = not (offset <= self.position[1] < canvh)
        noob = not (ooblr or oobud) #and (phstack != 0)
        coob = (ooblr and oobud)# or (phstack == 0)
        if not noob:
            if self.position[0] < offset:
                self.position[0] = offset
            elif self.position[0] >= canvw:
                self.position[0] = canvw - 1
            if self.position[1] < offset:
                self.position[1] = offset
            elif self.position[1] >= canvh:
                self.position[1] = canvh - 1
        self.field_of_view = fov * noob +  LR[fov] * ooblr + UD[fov] * oobud
        self.field_of_view *= (1 - coob)
        self.field_of_view += (fov + 8) * coob
        self.endurance -= consts.speedmod.get()



        x, y = (self.position[0]), (self.position[1])
        # case d'arrivée pathogen ?
        if self.infected == False:

            r = 10 #infection radius "global" arbitraire
            P = consts.canv.find_overlapping(x - r, y - r, x + r, y + r)
            t = len(P)+1
            for j in range(len(P)):
                if ("pathogen" in consts.canv.gettags(P[j])):
                    t = j
            if t < len(P):
                patho = consts.Dobj[P[t]]
                self.get_infected(patho)
                patho.quantity += -1
                if patho.quantity == 0:
                    consts.canv.delete(patho.id)
                    consts.Dobj.pop(patho.id)
        # case d'arrivée portail ?
        Port = consts.canv.find_overlapping(x - ANTR, y - ANTR, x + ANTR, y + ANTR)
        
        t = len(Port)+1
        for j in range(len(Port)):
            
            if ("portal" in consts.canv.gettags(Port[j])):
                t = j
        if t < len(Port):
            portal = consts.Dobj[Port[t]]
            portal.switch(self)
            portal.capacity += -1
            portal.other_portal.capacity += -1
            if portal.capacity == 0:
                consts.canv.delete(portal.id)
                consts.canv.delete(portal.other_portal.id)
                consts.Dobj.pop(portal.id)
                consts.Dobj.pop(portal.other_portal.id)
