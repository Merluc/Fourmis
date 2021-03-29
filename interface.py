import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import classes as cls
import numpy as np
import consts


idle_func_id = 0
flag_portal = 0
flag_sel = 0
current_obj = 0
tv1=tk.StringVar()
tv2=tk.StringVar()
tv3=tk.StringVar()
tv4=tk.StringVar()
tv5=tk.StringVar()
obswidth = 11
MIDOBS = (obswidth // 2) + 3
ARROW = tk.PhotoImage(file="arrow.png")
flag_defaut = 0
timer = 1000

def place_nest(event=False, ex=-1, ey=-1, fac=-1, res=-1, nsp=-1, sr=-1):
    """
    Cette fonction permet de bind au clic de souris la création
    d'un nid de fourmis

    Parameters
    ----------
    event : clic de souris

    Returns
    -------
    None.

    """
    canv = consts.canv
    rad = consts.NESTR * consts.vzoom
    if event:
        x, y = canv.canvasx(event.x), canv.canvasy(event.y)
        fac = consts.n_faction
        res = consts.n_res
        nsp = consts.n_spawn
        sr = consts.n_soldier
    else:
        x, y = ex, ey
    pos = [x - rad, y - rad, x + rad, y + rad]
    if canv.find_overlapping(*pos):
        return(1)
    oid = canv.create_oval(*pos, fill=fac, tags=("nest", fac))
    consts.Dobj[oid] = cls.Nest(pos, oid, fac, res, nsp, sr)
    consts.nest += [consts.Dobj[oid]]
    if event:
        tmp = consts.Dobj[oid].resources
        consts.Dobj[oid].spawn_ants()
        consts.Dobj[oid].resources = tmp
    return consts.Dobj[oid]



def create_ant(P, fac, role):
    """
    Cette fonction permet la création d'une fourmi

    Parameters
    ----------
    P : tuple (x1,y1,x2,y2)
    P represente le rectangle englobant la fourmi

    faction: string
    Donne la faction de la fourmi

    role : string
    Précise s'il s'agit d'une fourmi guerrière ou travailleuse

    Returns
    -------
    Retourne l'id dans le canvas de la création de la fourmi.

    """
    if role == "worker":
        o = consts.canv.create_oval(*P, fill=fac, tags=("ant", fac, role))
    else:
        o = consts.canv.create_rectangle(*P, fill=fac, tags=("ant", fac, role))
    return o


def place_resource(event=False, ex=-1, ey=-1, qty=consts.r_qty):
    """
    Cette fonction permet de bind au clic de souris la création
    d'une ressource

    Parameters
    ----------
    event : clic de souris

    Returns
    -------
    None.

    """
    canv = consts.canv
    rad = 20 * consts.vzoom
    if event:
        x, y = canv.canvasx(event.x), canv.canvasy(event.y)
    else:
        x, y = ex, ey
    pos = [x - rad, y - rad, x + rad, y + rad]
    if canv.find_overlapping(*pos):
        return(1)
    oid = canv.create_oval(*pos, fill="green", tags=("resource"))
    consts.mat[int(pos[0]):int(pos[0]) + rad * 2, int(pos[1]):int(pos[1]) + rad * 2] = 0
    consts.Dobj[oid] = cls.Resource(pos, oid, qty)
    return consts.Dobj[oid]


def place_pathogen(event=False, ex=-1, ey=-1, ir=-1, it=-1, kr=-1, rd=-1,
                   qty=-1):
    """
    Cette fonction permet de bind au clic de souris la création
    d'un pathogène

    Parameters
    ----------
    event : clic de souris

    Returns
    -------
    None.

    """
    canv = consts.canv
    rad = 10 * consts.vzoom
    if event:
        x, y = canv.canvasx(event.x), canv.canvasy(event.y)
        ir = consts.p_infra
        it = consts.p_incutime
        kr = consts.p_killra
        rd = consts.p_infection_radius
        qty = consts.p_qty
    else:
        x, y = ex, ey
    pos = [x - rad, y - rad, x + rad, y + rad]
    if canv.find_overlapping(*pos):
        return(1)
    oid = canv.create_oval(*pos, fill="brown", tags="pathogen")
    consts.mat[int(pos[0]):int(pos[1]) + rad * 2, int(pos[0]):int(pos[1]) + rad * 2] = 0
    consts.Dobj[oid] = cls.Pathogen(pos, oid, ir, it, kr,rd, qty)
    return consts.Dobj[oid]


def bresenham(point1, point2):
    """Algo de bresenham pour le trace de segment entre le point1 et le point2.
    """
    L = []
    xa, ya, xb, yb = point1[0], point1[1], point2[0], point2[1]
    dx = xb - xa
    dy = yb - ya
    x = xa
    y = ya
    vx = int(dx >= 0) - int(dx < 0)
    vy = int(dy >= 0) - int(dy < 0)
    if dx == 0:
        for i in range(ya, yb + vy, vy):
            L += [[xa, i]]
    elif abs(dy / dx) <= 1:
        dec = dx - (dy << 1)
        while abs(x - xa) <= abs(dx):
            L += [[x, y]]
            if dec < 0:
                if vx == 1:
                    dec += (dx << 1)
                else:
                    dec -= (dx << 1)
                y += vy
            dec -= (dy << 1) * vy
            x += vx
    else:
        dec = dy - (dx << 1)
        while abs(y - ya) <= abs(dy):
            L += [[x, y]]
            if dec < 0:
                dec += (dy << 1) * vy
                x += vx
            dec -= (dx << 1) * vx
            y += vy
    return L

def place_obstacle(event):
    """
    Cette fonction permet de bind au clic de souris la création
    d'un obstacle

    Parameters
    ----------
    event : clic de souris

    Returns
    -------
    None.

    """
    canv = event.widget
    canv.bind('<B1-Motion>', place_obstacle_mid)
    canv.bind('<ButtonRelease-1>', place_obstacle_end)
    consts.DEBRECTOBST += [[canv.canvasx(event.x), canv.canvasy(event.y)]]



def place_obstacle_mid(event):
    """
    Premier point du placement de l'obstacle'

    """
    canv = event.widget
    if len(consts.TEMPFORGUI) > 0:
        canv.delete(consts.TEMPFORGUI[-1])
        consts.TEMPFORGUI.pop()
    x, y = canv.canvasx(event.x), canv.canvasy(event.y)
    x1, y1 = consts.DEBRECTOBST[-1]
    t = ("obstacle",)
    ow = obswidth
    consts.TEMPFORGUI += [canv.create_line(x, y, x1, y1, width=ow, tags=t)]

def place_obstacle_end(event=False, oid=-1, pos=-1):
    """
    Tracer de l'obstacle entier
    """
    if event:
        oid = consts.TEMPFORGUI[-1]
        consts.TEMPFORGUI = []
        consts.DEBRECTOBST = []
        event.widget.unbind('<B1-Motion>')
        event.widget.unbind('<ButtonRelease-1>')
        pos = event.widget.coords(oid)
    x1, y1, x2, y2 = pos
    x1 = round(x1)
    y1 = round(y1)
    x2 = round(x2)
    y2 = round(y2)
    Lx1 = [x1 + i for i in range(1 - MIDOBS, MIDOBS)]
    Lx2 = [x2 + i for i in range(1 - MIDOBS, MIDOBS)]
    Ly1 = [y1 + i for i in range(1 - MIDOBS, MIDOBS)]
    Ly2 = [y2 + i for i in range(1 - MIDOBS, MIDOBS)]
    Lbres = []
    for x, y, z, t in zip(Lx1, Ly1, Lx2, Ly2):
        Lbres += bresenham([x, y], [z, t])
    for x, y in Lbres:
        consts.mat[x % consts.canvw][y % consts.canvh] = -1
    consts.Dobj[oid] = cls.Obstacle(pos, oid)
    return consts.Dobj[oid]

def place_eau(event):
    """
    Cette fonction permet de bind au clic de souris la création
    d'un obstacle d'eau

    Parameters
    ----------
    event : clic de souris

    Returns
    -------
    None.

    """
    canv = event.widget
    canv.bind('<B1-Motion>', place_eau_mid)
    canv.bind('<ButtonRelease-1>', place_eau_end)
    consts.DEBRECTOBST += [[canv.canvasx(event.x), canv.canvasy(event.y)]]


def place_eau_mid(event):
    """
    Premier point du placement de l'eau'

    """
    canv = event.widget
    if len(consts.TEMPFORGUI) > 0:
        canv.delete(consts.TEMPFORGUI[-1])
        consts.TEMPFORGUI.pop()
    x, y = canv.canvasx(event.x), canv.canvasy(event.y)
    x1, y1 = consts.DEBRECTOBST[-1]
    t = ("water",)
    ow = obswidth
    consts.TEMPFORGUI += [canv.create_line(x, y, x1, y1, width=ow, fill="blue", tags=t)]

def place_eau_end(event):
    """

    Tracer de l'eau entiere

    """
    oid = consts.TEMPFORGUI[-1]
    consts.TEMPFORGUI = []
    consts.DEBRECTOBST = []
    event.widget.unbind('<B1-Motion>')
    event.widget.unbind('<ButtonRelease-1>')
    pos = event.widget.coords(oid)
    x1, y1, x2, y2 = pos
    x1 = round(x1)
    y1 = round(y1)
    x2 = round(x2)
    y2 = round(y2)
    Lx1 = [x1 + i for i in range(1 - MIDOBS, MIDOBS)]
    Lx2 = [x2 + i for i in range(1 - MIDOBS, MIDOBS)]
    Ly1 = [y1 + i for i in range(1 - MIDOBS, MIDOBS)]
    Ly2 = [y2 + i for i in range(1 - MIDOBS, MIDOBS)]
    Lbres = []
    for x, y, z, t in zip(Lx1, Ly1, Lx2, Ly2):
        Lbres += bresenham([x, y], [z, t])
    for x, y in Lbres:
        consts.mat[x % consts.canvw][y % consts.canvh] = -1
    consts.Dobj[oid] = cls.Water(pos, oid,5)

def place_creusable(event):
    """
    Cette fonction permet de bind au clic de souris la création
    d'un obstacle creusable

    Parameters
    ----------
    event : clic de souris

    Returns
    -------
    None.

    """
    canv = event.widget
    canv.bind('<B1-Motion>', place_creusable_mid)
    canv.bind('<ButtonRelease-1>', place_creusable_end)
    consts.DEBRECTOBST += [[canv.canvasx(event.x), canv.canvasy(event.y)]]


def place_creusable_mid(event):
    """
    Premier point du placement du mur creusable

    """
    canv = event.widget
    if len(consts.TEMPFORGUI) > 0:
        canv.delete(consts.TEMPFORGUI[-1])
        consts.TEMPFORGUI.pop()
    x, y = canv.canvasx(event.x), canv.canvasy(event.y)
    x1, y1 = consts.DEBRECTOBST[-1]
    t = ("diggable",)
    ow = obswidth
    consts.TEMPFORGUI += [canv.create_line(x, y, x1, y1, width=ow, fill="brown", tags=t)]

def place_creusable_end(event):
    """
    Trace le mur creusable en entier

    """
    oid = consts.TEMPFORGUI[-1]
    consts.TEMPFORGUI = []
    consts.DEBRECTOBST = []
    event.widget.unbind('<B1-Motion>')
    event.widget.unbind('<ButtonRelease-1>')
    pos = event.widget.coords(oid)
    x1, y1, x2, y2 = pos
    x1 = round(x1)
    y1 = round(y1)
    x2 = round(x2)
    y2 = round(y2)
    Lx1 = [x1 + i for i in range(1 - MIDOBS, MIDOBS)]
    Lx2 = [x2 + i for i in range(1 - MIDOBS, MIDOBS)]
    Ly1 = [y1 + i for i in range(1 - MIDOBS, MIDOBS)]
    Ly2 = [y2 + i for i in range(1 - MIDOBS, MIDOBS)]
    Lbres = []
    for x, y, z, t in zip(Lx1, Ly1, Lx2, Ly2):
        Lbres += bresenham([x, y], [z, t])
    for x, y in Lbres:
        consts.mat[x % consts.canvw][y % consts.canvh] = -1
    consts.Dobj[oid] = cls.DiggableWall(pos, oid,5)



def place_portal(event=False, ex=-1, ey=-1):
    """
    Cette fonction permet de bind au clic de souris la création
    d'une paire de portail

    Parameters
    ----------
    event : clic de souris

    Returns
    -------
    None.

    """
    global flag_portal, tmpportal
    canv = consts.canv
    rad = 20 * consts.vzoom
    if event:
        x, y = canv.canvasx(event.x), canv.canvasy(event.y)
    else:
        x, y = ex, ey
    pos = [x - rad, y - rad, x + rad, y + rad]
    if canv.find_overlapping(*pos):
        return(1)
    oid = canv.create_oval(*pos, fill="purple", width=3, tags=("portal"))
    if flag_portal:
        pos2 = tmpportal[1] - rad, tmpportal[2] - rad, tmpportal[1] + rad, tmpportal[2] + rad
        canv.addtag_closest(oid, tmpportal[1], tmpportal[2])
        canv.addtag_closest(tmpportal[0], x, y)
        flag_portal = 0
        boop = cls.SpacePortal(pos, oid, consts.pt_cap, consts.pt_load, None)
        boop2 = cls.SpacePortal(pos2, tmpportal[0], consts.pt_cap, consts.pt_load, boop)
        boop.other_portal = boop2
        consts.Dobj[tmpportal[0]] = boop2
        consts.Dobj[oid] = boop
    else:
        tmpportal = (oid, x, y)
        flag_portal = 1
    # consts.mat[int(pos[0]):int(pos[0]) + rad * 2, int(pos[0]):int(pos[0]) + rad * 2] = 0
    return oid




def param_defaut(widget):
    """
    Permet d'afficher sur le latéral gauche, les paramètres par défauts
    de certains objets, ainsi que de les modifier

    Parameters
    ----------
    widget : tk.widget()
        Panneau latéral

    Returns
    -------
    None.

    """

    global flag_defaut,flag_sel
    if flag_defaut == 1:
        consts.sideres.forget()
        flag_defaut = 0
    elif flag_defaut == 2:
        consts.sidenest.forget()
        flag_defaut = 0
    elif flag_defaut == 3:
        consts.sidepath.forget()
        flag_defaut = 0
    elif flag_defaut == 4:
        consts.sideport.forget()
        flag_defaut = 0
    elif flag_sel == 1:
        consts.sideres.forget()
        flag_sel = 0
    elif flag_sel == 2:
        consts.sidenest.forget()
        flag_sel = 0
    elif flag_sel == 3:
        consts.sidepath.forget()
        flag_sel = 0
    elif flag_sel == 4:
        consts.sideport.forget()
        flag_sel = 0
    name=widget.cget("text")
    if name == "resource":
        consts.sideres.pack(side="left", fill="both", expand=True)
        flag_defaut = 1
        tv1.set(str(consts.r_qty))
    elif name == "nest":
        consts.sidenest.pack(side="left", fill="both", expand=True)
        flag_defaut = 2
        tv1.set(str(consts.n_faction))
        tv2.set(consts.n_res)
        tv3.set(consts.n_spawn)
        tv4.set(consts.n_soldier)
    elif name == "pathogen":
        consts.sidepath.pack(side="left", fill="both", expand=True)
        flag_defaut = 3
        tv1.set(str(consts.p_infra))
        tv2.set(consts.p_incutime)
        tv3.set(consts.p_killra)
        tv4.set(consts.p_infection_radius)
        tv5.set(consts.p_qty)
    elif name == "portal":
        consts.sideport.pack(side="left", fill="both", expand=True)
        flag_defaut = 4
        tv2.set(consts.pt_load)
        tv1.set(consts.pt_cap)



def select_param(event):
    """
    Cette fonction permet pour l'objet selectionné de modifier le panel
    latéral gauche montrant ses caractéristiques

    Parameters
    ----------
    event : clic de souris

    Returns
    -------
    None.

    """
    global flag_sel,current_obj,tv1,tv2,tv3,tv4,tv5,flag_defaut

    if flag_defaut == 1:
        consts.sideres.forget()
        flag_defaut = 0
    elif flag_defaut == 2:
        consts.sidenest.forget()
        flag_defaut = 0
    elif flag_defaut == 3:
        consts.sidepath.forget()
        flag_defaut = 0
    elif flag_defaut == 4:
        consts.sideport.forget()
        flag_defaut = 0
    elif flag_sel == 1:
        consts.sideres.forget()
        flag_sel = 0
    elif flag_sel == 2:
        consts.sidenest.forget()
        flag_sel = 0
    elif flag_sel == 3:
        consts.sidepath.forget()
        flag_sel = 0
    elif flag_sel == 4:
        consts.sideport.forget()
        flag_sel = 0

    canv = event.widget
    if current_obj:
        canv.itemconfigure(current_obj.id,outline="black")
    x, y = canv.canvasx(event.x), canv.canvasy(event.y)
    sel = canv.find_closest(x, y)
    canv.itemconfigure(sel[0],outline="blue")
    print(sel[0])
    current_obj = consts.Dobj[sel[0]]

    if canv.gettags(sel[0])[0] == "resource":
        consts.sideres.pack(side="left", fill="both", expand=True)
        flag_sel = 1
        tv1.set(str(current_obj.quantity))
    elif canv.gettags(sel[0])[0] == "nest":
        consts.sidenest.pack(side="left", fill="both", expand=True)
        flag_sel = 2
        tv1.set(str(current_obj.faction))
        tv2.set(current_obj.resources)
        tv3.set(current_obj.spawn_number)
        tv4.set(current_obj.soldier_rate)
    elif canv.gettags(sel[0])[0] == "pathogen":
        consts.sidepath.pack(side="left", fill="both", expand=True)
        flag_sel = 3
        tv1.set(str(current_obj.infection_rate))
        tv2.set(current_obj.incubation_time)
        tv3.set(current_obj.kill_rate)
        tv4.set(current_obj.infection_radius)
        tv5.set(current_obj.quantity)
    elif canv.gettags(sel[0])[0] == "portal":
        consts.sideport.pack(side="left", fill="both", expand=True)
        flag_sel = 4
        tv2.set(current_obj.loading_time)
        tv1.set(current_obj.capacity)
    print (consts.n_faction)

def callback_cbb(event,parameter,label):
    global flag_sel,flag_defaut
    """
    Cette fonction est un callback de la selection d'une valeur dans la
    combobox "parameter" representant le parametre "label". Elle permet
    la modification de certaines caractéristiques de l'objet courant.
    Ou selon le cas de modifier une valeut par défaut

    Parameters
    ----------
    event : selection de combobox

    parameter : tk.combobox
        Parameter est la combobox du parametre selectionné

    label : tk.label
        Utilisé pour recuperer le nom du paramètre

    Returns
    -------
    None.

    """
    param=label.cget("text").lower()
    param=param.replace(" ", "_")
    if flag_sel > 0:
        if param =="faction":
            consts.canv.itemconfigure(current_obj.id,fill=parameter.get())
            current_obj.__dict__[param] = parameter.get()
        elif param == "capacity":
            current_obj.__dict__[param] = int(parameter.get())
            current_obj.other_portal.__dict__[param] = int(parameter.get())
        elif param == "loading_time":
            current_obj.__dict__[param] = int(parameter.get())
            current_obj.other_portal.__dict__[param] = int(parameter.get())
        else:
            current_obj.__dict__[param]= int(parameter.get())
    elif flag_defaut > 0:
        p = parameter.get()
        if flag_defaut == 1:
            consts.r_qty=int(p)
        elif flag_defaut == 2:
            if param == "faction":
                consts.n_faction = p
            elif param == "resources":
                consts.n_res = int(p)
            elif param == "spawn_number":
                consts.n_spawn = int(p)
            elif param == "soldier_rate":
                consts.n_soldier = int(p)
        elif flag_defaut ==3 :
            if param == "infection_rate":
                consts.p_infra = int(p)
            elif param == "incubation_time":
                consts.p_incutime = int(p)
            elif param == "kill_rate":
                consts.p_killra = int(p)
            elif param == "infection_radius":
                consts.p_infection_radius = int(p)
            elif param == "quantity":
                consts.p_qty = int(p)
        elif flag_defaut == 4:
            if param == "capacity":
                consts.pt_cap = int(p)
            elif param == "loading_time":
                consts.pt_load = int(p)




def erase(event):
    """
    Cette fonction permet de bind au clic de souris la suppression d'un
    objet

    Parameters
    ----------
    event : clic de souris

    Returns
    -------
    None.

    """
    canv = event.widget
    x, y = canv.canvasx(event.x), canv.canvasy(event.y)
    obj = canv.find_overlapping(x, y, x, y)
    L = canv.gettags(obj)
    if L:
        if L[0] == "nest":
            for a in cls.ANTS:
                if a.nid_id.id == obj[0]:
                    canv.delete(a.id)
    canv.delete(obj)


def supp_all():
    """

    Permet de reset le canvas et donc la simulation

    Returns
    -------
    None.

    """
    consts.canv.delete("all")
    consts.mat = np.ones((consts.canvw, consts.canvh))
    cls.ANTS = []
    consts.Dobj = {}


def add_resource():
    """
    Permet d'ajouter directement 10 de ressources a chacunes des fourmis

    Returns
    -------
    None.

    """
    for ant in cls.ANTS:
        ant.resources += 10


def start_sim():
    """
    Callback du bouton permettant de commencer la simulation. Permet donc de
    lancer la simulation

    Returns
    -------
    None.

    """
    global idle_func_id, timer
    timer -= consts.speedmod.get()
    if timer <= 0:
        for i in consts.nest:
            i.spawn_ants()
        timer = 1000
    consts.mat = consts.mat*((consts.mat**2)*19 + 2)/((consts.mat**2)*20 + 1)
    for ant in cls.ANTS:
        ant.move()
    idle_func_id = consts.canv.after_idle(start_sim)


def zoomer(event):
    """
    Callback permettant au bouton zoom de zoomer

    Parameters
    ----------
    event : clic sur le bouton zoom

    Returns
    -------
    None.

    """
    canv = event.widget
    x, y = canv.canvasx(event.x), canv.canvasy(event.y)
    canv.scale("all", x, y, 1.1, 1.1)
    consts.vzoom *= 1.1

def dezoomer(event):
    """
    Callback permettant au bouton dezoom de dezoomer

    Parameters
    ----------
    event : clic sur le bouton dezoom

    Returns
    -------
    None.

    """
    canv = event.widget
    x, y = canv.canvasx(event.x), canv.canvasy(event.y)
    canv.scale("all", x, y, 0.9, 0.9)
    consts.vzoom *= 0.9



def main_func():
    """
    Fonction permettant l'affichage et l'utilisation de l'interface

    Returns
    -------
    None.

    """
    root = consts.root
    canvfr = consts.canvfr
    canv = consts.canv
    root.geometry(str(consts.rootw)+"x"+str(consts.rooth)+"+100+100")
    root.minsize(consts.rootw, consts.rooth)
    root.maxsize(consts.rootw, consts.rooth)
    root.title("Antz")

    # Canvas
    canv.pack()

    # Toolbar
    toolfr = tk.Frame(root)

    def bindfunc(func, Mfunc=None):
        def ffunc():
            canv.bind('<1>', func)
            if Mfunc is None:
                canv.unbind('<B1-Motion>')
            else:
                canv.bind('<B1-Motion>', Mfunc)
        return ffunc


    # Bouton Nid
    nbutt = tk.Button(toolfr, text="Nest", command=bindfunc(place_nest))
    nbutt.pack(side="left")

    nestopt = tk.Button(toolfr, image=ARROW, text="nest", command= lambda : param_defaut(nestopt))
    nestopt.pack(side="left")
    # Bouton Ressource
    rbutt = tk.Button(toolfr, text="Resource", command=bindfunc(place_resource))
    rbutt.pack(side="left")
    resopt = tk.Button(toolfr, image=ARROW, text="resource", command= lambda : param_defaut(resopt))
    resopt.pack(side="left")
    # Bouton Pathogene
    pbutt = tk.Button(toolfr, text="Pathogen", command=bindfunc(place_pathogen))
    pbutt.pack(side="left")
    pathopt = tk.Button(toolfr, image=ARROW, text="pathogen" ,command= lambda : param_defaut(pathopt))
    pathopt.pack(side="left")
    # Bouton Portail
    spbutt = tk.Button(toolfr, text="Portal",
                      command=bindfunc(place_portal))
    spbutt.pack(side="left")
    spopt = tk.Button(toolfr, image=ARROW, text="portal", command= lambda : param_defaut(spopt))
    spopt.pack(side="left")
    # Bouton Mur
    obutt = tk.Button(toolfr, text="Wall", command=bindfunc(place_obstacle,
                                                                place_obstacle))
    obutt.pack(side="left")

    # Bouton Mur Creusable
    dobutt = tk.Button(toolfr, text="Diggable Wall", command=bindfunc(place_creusable,
                                                                place_creusable))
    dobutt.pack(side="left")
    # Bouton Eau
    wobutt = tk.Button(toolfr, text="Water", command=bindfunc(place_eau,
                                                                place_eau))
    wobutt.pack(side="left")
    # Bouton Parametre_Selection
    sbutt = tk.Button(toolfr, text="Select",
                      command=bindfunc(select_param))
    sbutt.pack(side="left")

    # Bouton Effacer
    ebutt = tk.Button(toolfr, text="Erase",
                      command=bindfunc(erase, erase))
    ebutt.pack(side="left")
    # Bouton Zoom
    zbutt = tk.Button(toolfr, text="Zoom",
                      command=bindfunc(zoomer))
    zbutt.pack(side="left")
    # Bouton Dezoom
    dzbutt = tk.Button(toolfr, text="Dezoom",
                      command=bindfunc(dezoomer))
    dzbutt.pack(side="left")



    # Commandbar
    cmdfr = tk.Frame(root)
    sbutt = tk.Button(cmdfr, text="Start", command=start_sim)
    sbutt.pack(side="left")
    pauseb = tk.Button(cmdfr, text="Pause",
                       command=lambda: consts.canv.after_cancel(idle_func_id))
    pauseb.pack(side="left")

    debugresource = tk.Button(cmdfr, text="add resource", command=add_resource)
    debugresource.pack(side="left")

    speedmod = consts.speedmod
    speedscale = tk.Scale(cmdfr, orient='horizontal', from_=0.5, to=3,
                          resolution=0.5, tickinterval=0.5, length = 150,
                          variable=speedmod)
    speedscale.pack(side="right")


    # Sidebar Nid
 # Sidebar Nid
    t1 = tk.Label(consts.sidenest, text="Faction")
    b1 = ttk.Combobox(consts.sidenest, width=6, textvariable=tv1, values=[ "red", "blue", "green"])

    t2 = tk.Label(consts.sidenest, text="Resources")
    b2 = ttk.Combobox(consts.sidenest, width=3, textvariable=tv2, values=[ 50, 100, 150, 200, 250, 300])

    t3 = tk.Label(consts.sidenest, text="Spawn Number")
    b3 = ttk.Combobox(consts.sidenest, width=3, textvariable=tv3, values=[ 5, 6, 7, 8, 9, 10])

    t4 = tk.Label(consts.sidenest, text="Soldier Rate")
    b4 = ttk.Combobox(consts.sidenest, width=3, textvariable=tv4, values=[ 10, 20, 30, 40, 50])

    t1.grid(column=0,row=0)
    b1.grid(column=1,row=0)
    t2.grid(column=0,row=1)
    b2.grid(column=1,row=1)
    t3.grid(column=0,row=2)
    b3.grid(column=1,row=2)
    t4.grid(column=0,row=3)
    b4.grid(column=1,row=3)


    # Sidebar Ressource
    t5 = tk.Label(consts.sideres, text="Quantity")
    b5 = ttk.Combobox(consts.sideres, width=3, textvariable = tv1, values= [100, 200, 300, 500, 1000])

    t5.grid(column=0, row=0)
    b5.grid(column=1, row=0)


    # Sidebar Pathogene
    t6 = tk.Label(consts.sidepath, text="Infection Rate")
    b6 = ttk.Combobox(consts.sidepath, width=3, textvariable = tv1, values= [1,2,5,10,20])

    t7 = tk.Label(consts.sidepath, text="Incubation Time")
    b7 = ttk.Combobox(consts.sidepath, width=3, textvariable = tv2, values= [1,5,10,30,50,100, 200, 300])

    t8 = tk.Label(consts.sidepath, text="Kill Rate")
    b8 = ttk.Combobox(consts.sidepath, width=3, textvariable = tv3, values= [1,2,5,10,20])

    t9 = tk.Label(consts.sidepath, text="Infection Radius")
    b9 = ttk.Combobox(consts.sidepath, width=3, textvariable = tv4, values= [10,20,30,40,50])

    t10 = tk.Label(consts.sidepath, text="Quantity")
    b10 = ttk.Combobox(consts.sidepath, width=3, textvariable = tv5, values= [10 ,20 ,50 ,100, 200, 300])


    t6.pack(side="top")
    b6.pack(side="top")
    t7.pack(side="top")
    b7.pack(side="top")
    t8.pack(side="top")
    b8.pack(side="top")
    t9.pack(side="top")
    b9.pack(side="top")
    t10.pack(side="top")
    b10.pack(side="top")

    # Sidebar Portail
    t11 = tk.Label(consts.sideport, text="Capacity")
    b11 = ttk.Combobox(consts.sideport, width=3, textvariable = tv1, values= [10,20,50,100, 200, 300,400])

    t12 = tk.Label(consts.sideport, text="Loading Time")
    b12 = ttk.Combobox(consts.sideport, width=3, textvariable = tv2, values= [10,20,30])


    t11.pack(side="top")
    b11.pack(side="top")
    t12.pack(side="top")
    b12.pack(side="top")

    # Binding Combobox selection
    b1.bind('<<ComboboxSelected>>',lambda X : callback_cbb(X,b1,t1))
    b2.bind("<<ComboboxSelected>>",lambda X : callback_cbb(X,b2,t2))
    b3.bind("<<ComboboxSelected>>",lambda X : callback_cbb(X,b3,t3))
    b4.bind("<<ComboboxSelected>>",lambda X : callback_cbb(X,b4,t4))
    b5.bind("<<ComboboxSelected>>",lambda X : callback_cbb(X,b5,t5))
    b6.bind("<<ComboboxSelected>>",lambda X : callback_cbb(X,b6,t6))
    b7.bind("<<ComboboxSelected>>",lambda X : callback_cbb(X,b7,t7))
    b8.bind("<<ComboboxSelected>>",lambda X : callback_cbb(X,b8,t8))
    b9.bind("<<ComboboxSelected>>",lambda X : callback_cbb(X,b9,t9))
    b10.bind("<<ComboboxSelected>>",lambda X : callback_cbb(X,b10,t10))
    b11.bind("<<ComboboxSelected>>",lambda X : callback_cbb(X,b11,t11))
    b12.bind("<<ComboboxSelected>>",lambda X : callback_cbb(X,b12,t12))

    #Bindin combobox "entry"
    b1.bind('<Return>',lambda X : callback_cbb(X,b1,t1))
    b2.bind('<Return>',lambda X : callback_cbb(X,b2,t2))
    b3.bind('<Return>',lambda X : callback_cbb(X,b3,t3))
    b4.bind('<Return>',lambda X : callback_cbb(X,b4,t4))
    b5.bind('<Return>',lambda X : callback_cbb(X,b5,t5))
    b6.bind('<Return>',lambda X : callback_cbb(X,b6,t6))
    b7.bind('<Return>',lambda X : callback_cbb(X,b7,t7))
    b8.bind('<Return>',lambda X : callback_cbb(X,b8,t8))
    b9.bind('<Return>',lambda X : callback_cbb(X,b9,t9))
    b10.bind('<Return>',lambda X : callback_cbb(X,b10,t10))
    b11.bind('<Return>',lambda X : callback_cbb(X,b11,t11))
    b12.bind('<Return>',lambda X : callback_cbb(X,b12,t12))

    # Barre de menus
    menu = tk.Menu(root)
    root['menu'] = menu
    fichier = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label='File', menu=fichier, underline=0)
    fichier.add_command(label='New', command=supp_all)

    def savefunc():
        """
        Fonction permettant de sauvegarder une simulation

        Returns
        -------
        None.

        """
        savename = filedialog.asksaveasfilename()
        if savename == '' or savename == ():
            return
        oof = open(savename, "w+")
        L = canv.find_all()
        for obj in L:
            ch = str(obj) + " "
            tags = canv.gettags(obj)
            obtype = str(tags[0])
            if "worker" in tags:
                ch += "worker "
            elif "soldier" in tags:
                ch += "soldier "
            else:
                ch += obtype + " "
            realob = consts.Dobj[obj]
            for attribute in realob.__dict__:
                if attribute == "nid_id":
                    ch += str(realob.nid_id.id) + " "
                elif attribute == "other_portal":
                    try:
                        ch += str(realob.other_portal.id) + " "
                    except:
                        ch += "None "
                elif attribute == "pathogen":
                    if realob.pathogen != -1:
                        ch += str(realob.pathogen.id) + " "
                    else:
                        ch += "-1 "
                else:
                    field = str(realob.__dict__[attribute])
                    field = field.replace("(","").replace(")","")
                    field = field.replace("[","").replace("]","")
                    field = field.replace(",","")
                    ch += field + " "
            ch += "\n"
            oof.write(ch)
        oof.close()

    fichier.add_command(label="Save", command=savefunc)

    def errorMessage(errortext, errorhead="Erreur"):
        try:
            messagebox.showerror(errorhead, errortext)
        except tk.TclError:
            exit()
    def loadfunc():
        # TODO: gérer l'eau et les murs creusables
        filename = filedialog.askopenfilename()
        try:
            inf = open(filename, "r")
        except FileNotFoundError:
            supp_all()
            return
        except IOError:
            errorMessage("Erreur d'ouverture de fichier")
            return
        supp_all()
        corresp = {}
        toinfect = {}
        l = inf.readlines(1)
        while l and l != []:
            a = l[0].split()
            if a[1] == "nest":
                ax = (float(a[2]) + float(a[4])) / 2
                ay = (float(a[3]) + float(a[5])) / 2
                tmp = place_nest(False, ax, ay, a[7], int(a[8]), int(a[9]),
                                 int(a[10]))
                corresp[a[0]] = tmp
            if a[1] == "worker" or a[1] == "soldier":
                ax = float(a[3])
                ay = float(a[4])
                antr = cls.ANTR + (a[1] == "soldier")
                P = [ax - antr, ay - antr, ax + antr, ay + antr]
                tmp = create_ant(P, a[2], a[1])
                if a[1] == "worker":
                    newAnt = cls.WorkerAnt(a[2], [ax, ay], float(a[6]),
                                       int(a[7]), float(a[11]),
                                       float(a[12]),
                                       corresp[a[13]], tmp,
                                       float(a[14]))
                else:
                    newAnt = cls.SoldierAnt(a[2], [ax, ay], float(a[6]),
                                        int(a[7]), float(a[11]),
                                        float(a[12]),
                                        corresp[a[13]], tmp)
                cls.ANTS += [newAnt]
                consts.Dobj[tmp] = newAnt
                if a[10] in corresp:
                    newAnt.get_infected(consts.Dobj[corresp[a[10]]])
                    newAnt.incubation_time = a[9]
                elif a[10] != -1:
                    if a[10] in toinfect:
                        toinfect[a[10]] += [(newAnt, a[9])]
                    else:
                        toinfect[a[10]] = [(newAnt, a[9])]
            if a[1] == "resource":
                ax = (float(a[2]) + float(a[4])) / 2
                ay = (float(a[3]) + float(a[5])) / 2
                tmp = place_resource(False, ax, ay, float(a[-1]))
            if a[1] == "obstacle":
                pos = [a[2], a[3], a[4], a[5]]
                pos = [float(ad) for ad in pos]
                t = ("obstacle",)
                ow = obswidth
                oid = consts.canv.create_line(*pos, width=ow, tags=t)
                tmp = place_obstacle_end(False, oid, pos)
            if a[1] == "portal":
                ax = (float(a[2]) + float(a[4])) / 2
                ay = (float(a[3]) + float(a[5])) / 2
                tmp = place_portal(False, ax, ay)
            if a[1] == "pathogen":
                ax = (float(a[2]) + float(a[4])) / 2
                ay = (float(a[3]) + float(a[5])) / 2
                tmp = place_pathogen(False, ax, ay, float(a[7]), float(a[8]),
                                     float(a[9]), float(a[10]), float(a[11]))
                corresp[a[0]] = tmp
                # Bug: le pathogen ne s'attache pas bien à la fourmi
                if a[0] in toinfect:
                    for ant, incut in toinfect[a[0]]:
                        try:
                            ant.infected = True
                            ant.pathogen = consts.Dobj[tmp]
                            ant.incubation_time = incut
                        except:
                            print(a)
            l = inf.readlines(1)
        inf.close()

    fichier.add_command(label="Load", command=loadfunc)

    option = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Option", menu=option, underline=0)


    def opreswin():
        opwin = tk.Toplevel(root, height=300, width=400)
        opwin.lift()
        opwin.grab_set()
        tk.Label(opwin, text="Width: ").grid(row=0, column=0)
        tk.Label(opwin, text="Height: ").grid(row=1, column=0)
        wvar = tk.StringVar()
        hvar = tk.StringVar()
        tk.Entry(opwin, textvariable=wvar).grid(row=0, column=1)
        tk.Entry(opwin, textvariable=hvar).grid(row=1, column=1)

        def okfunc():
            try:
                neww = int(float(wvar.get()))
                newh = int(float(wvar.get()))
                consts.rootw = neww
                consts.rooth = newh
                consts.canvw = neww - 200
                consts.canvh = newh - 90
                root.minsize(consts.rootw, consts.rooth)
                root.maxsize(consts.rootw, consts.rooth)
                consts.root.geometry(str(neww)+"x"+str(newh)+"+100+100")
                consts.canv.config(width=neww-200, height=newh-90)
                opwin.grab_release()
                opwin.destroy()
            except:
                opwin.grab_release()
                opwin.destroy()

        def annfunc():
            opwin.grab_release()
            opwin.destroy()

        tk.Button(opwin, text="Ok", command=okfunc).grid(row=4, column=0)
        tk.Button(opwin, text="Annuler", command=annfunc).grid(row=4, column=1)

    option.add_command(label='Resize', command=opreswin)
    toolfr.pack(side="top", fill="both")
    cmdfr.pack(side="bottom")
    canvfr.pack(side="right")
    # sidefr.pack(side="left", fill="both", expand=True)

    tk.mainloop()
    exit()


if __name__ == "__main__":
    main_func()
