import streamlit as st
import random

st.title("S4A Probabilistic Cost Reduction Option Model (Option1)")

st.markdown("## Input Parameters")
st.markdown("### Apps")
n_apps = st.slider("Total number of apps", 0, 100000, 10000, 100)
apps_active_per_day = st.slider("Fraction of active apps per day", 0.0, 1.0, 0.25, 0.05)
hours_active_per_day = st.slider("Hours an app is active out of the 8 work hours in a day", 0, 8, 1, 0.1)
#n_active = st.slider("Number of active apps", 0, 10000, 300)
mem_idle = st.slider("Memory for a idle app", 0.0, 64.0, 0.2, 0.1)
mem_active = st.slider("Memory for an active app", 0.0, 64.0, 2.0, 0.1)

st.markdown("### System Specs")
n_nodes = st.slider("Total number of nodes", 0, 10000, 330)
MAX_MEM = st.slider("Max memory for a node", 1, 64, 16, 1)
#REQ_MEM = st.slider("Memory requests", 0.0, 64.0, 0.4, 0.1)

st.markdown("### Simulation Parameters")
n_iter = st.slider("Number of iterations", 0, 10000, 100)


n_active = int(round(n_apps * apps_active_per_day * hours_active_per_day / 8))

memory = [0,]*n_nodes

apps = [mem_idle,]*(n_apps-n_active) + [mem_active,]*n_active  

apps_per_node = n_apps // n_nodes

# partition by number of apps per node
def simulate():
    random.shuffle(apps)
    out_of_mem = False
    for i in range(n_nodes):
        total_mem = sum(apps[i*apps_per_node: (i + 1)*apps_per_node])
        if total_mem > MAX_MEM:
            out_of_mem = True
    return out_of_mem


out_of_mem = 0
for _ in range(n_iter):
    out_of_mem += simulate()

st.markdown("## Model Output")
st.write("Number of active apps", n_active)
st.write("P out of mem:", out_of_mem / n_iter)
st.write("Packing rate:", apps_per_node)

