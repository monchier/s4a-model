import streamlit as st
import random

st.title("S4A Probabilistic Cost Reduction Option Model (Option1)")

st.markdown("## Input Parameters")
st.markdown("### Apps")
N_APPS = st.slider("Total number of apps", 0, 100000, 10000, 100)
N_ACTIVE = st.slider("Number of active apps", 0, 10000, 300)
mem_idle = st.slider("Memory for a idle app", 0.0, 64.0, 0.2, 0.1)
mem_active = st.slider("Memory for an active app", 0.0, 64.0, 2.0, 0.1)

st.markdown("### System Specs")
N_NODES = st.slider("Total number of nodes", 0, 10000, 330)
MAX_MEM = st.slider("Max memory for a node", 1, 64, 16, 1)
#REQ_MEM = st.slider("Memory requests", 0.0, 64.0, 0.4, 0.1)

st.markdown("### Simulation Parameters")
ITER = st.slider("Number of iterations", 0, 10000, 100)


memory = [0,]*N_NODES

apps = [mem_idle,]*(N_APPS-N_ACTIVE) + [mem_active,]*N_ACTIVE  

apps_per_node = N_APPS // N_NODES




# partition by number of apps per node
def simulate():
    random.shuffle(apps)
    out_of_mem = False
    for i in range(N_NODES):
        total_mem = sum(apps[i*apps_per_node: (i + 1)*apps_per_node])
        if total_mem > MAX_MEM:
            out_of_mem = True
    return out_of_mem


out_of_mem = 0
for _ in range(ITER):
    out_of_mem += simulate()

st.markdown("## Model Output")
st.write("P out of mem:", out_of_mem / ITER)
st.write("Packing rate:", N_APPS / N_NODES)

