#
# Simulate user-defined current profile which takes parameters
#
import pybamm
import numpy as np


# create user-defined function
def my_fun(t, A, omega):
    return A * pybamm.sin(2 * np.pi * omega * t)


# choose amplitude and frequencies
A = pybamm.electrical_parameters.I_typ
frequencies = [0.1, 1]

# load models (need to create new instances of model, not copies)
pybamm.set_logging_level("INFO")
models = [None] * len(frequencies)
for i in range(len(frequencies)):
    models[i] = pybamm.lithium_ion.SPM()

# load parameter values and process models
param = models[0].default_parameter_values
for i, frequency in enumerate(frequencies):

    def current(t):
        return my_fun(t, A, frequency)

    param.update({"Current function [A]": current})
    param.process_model(models[i])

# discretise models
for model in models:
    # create geometry
    geometry = model.default_geometry
    param.process_geometry(geometry)
    mesh = pybamm.Mesh(
        geometry, models[-1].default_submesh_types, model.default_var_pts
    )
    disc = pybamm.Discretisation(mesh, model.default_spatial_methods)
    disc.process_model(model)

# Example: simulate for 30 seconds
simulation_time = 30  # end time in seconds

# loop over frequencies
solutions = [None] * len(frequencies)
labels = [None] * len(frequencies)
for i, frequency in enumerate(frequencies):
    # need enough timesteps to resolve output
    npts = int(50 * simulation_time * frequency)
    t_eval = np.linspace(0, simulation_time, npts)
    solutions[i] = model.default_solver.solve(models[i], t_eval)
    labels[i] = "Frequency: {} Hz".format(frequency)

# plot
output_variables = ["Current [A]", "Terminal voltage [V]"]
plot = pybamm.QuickPlot(solutions, output_variables, labels)
plot.dynamic_plot()
