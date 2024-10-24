import pandas as pd
import plotly.express as px
import plotly.offline as pyo
import numpy as np


def iapp(e_ion, z):
    return 4e9 * e_ion**4 / z**2


def a0(wavelength):
    def a0_x(x):
        return np.sqrt(7.3e-19 * wavelength**2 * x)

    return a0_x

def kinE(wavelength):
    return 1/2 * 9.1e-31 * a0(wavelength)**2 * 3e8**2 /1.6e-19

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
ionization_data["I_app"] = iapp(ionization_data.W_ion, ionization_data.q+1)
ionization_data["element"] = ionization_data.name.map(
    lambda x: x.lstrip().split(" ")[0]
)
ionization_data["a0 (800nm)"] = ionization_data.I_app.map(a0(0.8))
ionization_data["a0 (1030nm)"] = ionization_data.I_app.map(a0(1.03))
ionization_data["Ekin (800nm)"] = ionization_data.I_app.map(kinE(0.8))
ionization_data["Ekin (1030nm)"] = ionization_data.I_app.map(kinE(1.03))

grps = ionization_data.groupby("Z")


# Calculate the x_positions for the bars
x_positions = []
group_labels = []
ticks = []
ticklabels = []
x0 = 0  # Initial x position
group_width = 1
colors = px.colors.sequential.YlGnBu


# Create a function to generate the plot based on the selected parameter
def generate_plot(parameter):
    if parameter == "a0_800":
        y_column = "a0 (800nm)"
        y_title = "appearance intensity (a0 @ 800nm)"
    elif parameter == "a0_1030":
        y_column = "a0 (1030nm)"
        y_title = "appearance intensity (a0 @ 1030nm)"
    elif parameter == "intensity":
        y_column = "I_app"
        y_title = "Intensity (W/cm^2)"
    else:
        raise ValueError("Invalid parameter")

    fig = px.bar(
        ionization_data,
        x="element",
        y=y_column,
        color="element",
        hover_name="name",
        hover_data={
            "I_app": ":.2e",
            "a0 (1030nm)": ":.2f",
            "a0 (800nm)": ":.2f",
            "W_ion": ":.2f",
            "Ekin (1030nm)": ":.2f",
            "Ekin (800nm)": ":.2f",
        },
        color_discrete_sequence=px.colors.qualitative.Prism,
        barmode="overlay",
        opacity=0.5,
        template="plotly_white",
    )
    fig.update_yaxes(exponentformat="e")
    fig.update_yaxes(title=y_title)
    fig.update_yaxes(showspikes=True, spikecolor="orange", spikethickness=2)
    if parameter in ["a0_800", "a0_1030"]:
        fig.update_yaxes(range=[0, 10])
    elif parameter == "intensity":
        # log scale
        fig.update_yaxes(type="log")
    pyo.plot(
        fig, filename=f"docs/index_{parameter.replace(' ', '_')}.html", auto_open=False
    )

    dropdown_menu = """
    <div class="dropdown">
        <button onclick="toggleDropdown()" class="dropbtn">Choose Plot</button>
        <div id="dropdown-content" class="dropdown-content">
            <a href="index_a0_800.html">a0 (800nm)</a>
            <a href="index_a0_1030.html">a0 (1030nm)</a>
            <a href="index_intensity.html">Intensity</a>
        </div>
    </div>
    <script>
        function toggleDropdown() {
            var dropdown = document.getElementById("dropdown-content");
            if (dropdown.style.display === "block") {
                dropdown.style.display = "none";
            } else {
                dropdown.style.display = "block";
            }
        }
    </script>
    <style>
        .dropdown {
            position: relative;
            display: inline-block;
        }
        .dropbtn {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border: none;
            cursor: pointer;
        }
        .dropdown-content {
            display: none;
            position: absolute;
            background-color: #f9f9f9;
            min-width: 160px;
            box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
            z-index: 1;
            left: 0;
        }
        .dropdown-content a {
            padding: 12px 16px;
            text-decoration: none;
            display: block;
            font-family: "Roboto", sans-serif; /* Change the font here */
        }
        .dropdown-content a:hover {
            background-color: #ddd;
        }
    </style>
     <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@400&display=swap">
    """

    # Embed the dropdown menu in the HTML file
    html_content = f"""
    <html>
    <head>
        <title>Plot: {parameter}</title>
    </head>
    <body>
        {dropdown_menu}
        {fig.to_html()}
    </body>
    </html>
    """

    with open(f"docs/index_{parameter.replace(' ', '_')}.html", "w") as f:
        f.write(html_content)


# Generate the three versions of the plot
generate_plot("a0_800")
generate_plot("a0_1030")
generate_plot("intensity")
