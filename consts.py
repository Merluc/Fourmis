import tkinter as tk
import numpy as np

root = tk.Tk()
root.title("test")
canvfr = tk.Frame(root)
rootw = 1000
rooth = 800
canvw = rootw - 200
canvh = rooth - 90
canv = tk.Canvas(canvfr, bg="white", width=canvw, height=canvh)
sidenest = tk.Frame(root)
sideres = tk.Frame(root)
sidepath = tk.Frame(root)
sideport = tk.Frame(root)
speedmod = tk.DoubleVar()
speedmod.set(1)
mat = np.ones((canvw, canvh))
NESTR = 25
Dobj = {}
vzoom = 1
nest = []
DEBRECTOBST = []
TEMPFORGUI = []


r_qty = 300
n_faction = "red"
n_res = 10
n_spawn = 10
n_soldier = 10
p_infra = 5
p_incutime=100
p_killra = 5
p_infection_radius = 5
p_qty = 10
pt_load = 10
pt_cap = 50
