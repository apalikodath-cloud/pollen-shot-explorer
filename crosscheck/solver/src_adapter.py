"""Adapter: run the main solver (src/flight.py) on the blind reference cases."""
import math
import numpy as np
from src import flight


def run(inputs, params):
    p = {"rho": params["rho"], "mass": params["m"], "radius": params["R"], "Cd": params["Cd"],
         "Cl": (params["c1"], params["Cl_max"]), "spin_decay_k": params["k_spin"],
         "g": params["g"], "eps_v": params["eps_v"]}
    e = math.radians(inputs["elev_deg"])
    v0 = inputs["v0_m_s"]
    vel = [v0 * math.cos(e), 0.0, v0 * math.sin(e)]
    w = inputs["S0"] * v0 / params["R"]
    omega = list(np.asarray(inputs["spin_axis"], float) * w)
    tr = flight.simulate([inputs["x0_m"], 0.0, inputs["z0_m"]], vel, omega, p,
                         wind=tuple(params["wind"]), t_max=10.0, z_ground=-0.05,
                         method="DOP853", rtol=1e-11, atol=1e-12)
    t = np.arange(0.0, tr.t[-1], 5e-4)
    y = tr.sol(t)
    return {"t": t, "x": y[0], "z": y[2], "vx": y[3], "vz": y[5]}
