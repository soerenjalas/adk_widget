import pandas as pd
import plotly.express as px
import plotly.offline as pyo
import numpy as np


def iapp(e_ion, z):
    return 4e9 * e_ion**4 / z**2


def a0(x):
    return np.sqrt(7.3e-19 * 0.8**2 * x)


def e_converter(x):
    return x.strip().replace("(", "").replace(")", "").replace("[", "").replace("]", "")


ionization_data = pd.read_csv(
    "ionization_data.txt",
    header=0,
    sep="|",
    names=["Z", "name", "q", "W_ion", "none"],
    converters={"W_ion": e_converter, "name": e_converter},
    # dtype={'W_ion':float}
)
ionization_data.W_ion = ionization_data.W_ion.astype(float)
ionization_data["I_app"] = iapp(ionization_data.W_ion, ionization_data.Z)
ionization_data["element"] = ionization_data.name.map(
    lambda x: x.lstrip().split(" ")[0]
)
ionization_data["a0 (800nm)"] = ionization_data.I_app.map(a0)

grps = ionization_data.groupby("Z")


# Calculate the x_positions for the bars
x_positions = []
group_labels = []
ticks = []
ticklabels = []
x0 = 0  # Initial x position
group_width = 1
colors = px.colors.sequential.YlGnBu


fig = px.bar(
    ionization_data,
    x="element",
    y="a0 (800nm)",
    color="element",
    #hover_data=["element", "name","I_app", "a0 (800nm)", "q", "W_ion", "Z"],
    hover_name="name",
    hover_data={'I_app': ':.2e', 'a0 (800nm)': ':.2f', 'W_ion': ':.2f'},
    color_discrete_sequence=px.colors.qualitative.Prism,
    barmode="overlay",
    opacity=0.5,
    template="plotly_white",
)
fig.update_yaxes(exponentformat="power")
# Customize the y-axis scale
#fig.update_yaxes(type="log", title="appearance intensity (W/cm^2)")
fig.update_yaxes(title="appearance intensity (a0 @ 800nm)")
fig.update_yaxes(showspikes=True, spikecolor="orange", spikethickness=2)
# ylimit
fig.update_yaxes(range=[0, 10])


# add horizontal lines
# a0 = 1
#fig.add_hline(y=1, line_width=1, line_dash="dash", line_color="black", annotation="Threshold")

#fig.show()
pyo.plot(fig, filename="docs/index.html", auto_open=False)
