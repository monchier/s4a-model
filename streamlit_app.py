import streamlit as st
import random
import math
from datetime import datetime
random.seed(datetime.now())

st.title("S4A Probabilistic Cost Reduction Option Model (Option1)")

st.markdown("## Input Parameters")
st.markdown("### Apps")
n_apps = st.slider("Total number of apps", 0, 100000, 10000, 100)
apps_active_per_day = st.slider("Fraction of active apps per day", 0.0, 1.0, 0.25, 0.05)
hours_active_per_day = st.slider("Hours an app is active out of the 8 work hours in a day", 0.0, 8.0, 1.0, 0.1)
mem_idle = st.slider("Memory for a idle app", 0.0, 64.0, 0.2, 0.1)
mem_active = st.slider("Memory for an active app", 0.0, 64.0, 2.0, 0.1)

st.markdown("### System Specs")
n_nodes = st.slider("Total number of nodes", 0, 1000, 300)
max_mem = st.slider("Max memory for a node", 1, 64, 16, 1)

per_node_system_cores = 1.0
per_node_system_memory = 0.5

manager_cores_active = 0.25
manager_memory_active = 0.5

manager_cores_idle = 0.05
manager_memory_idle = 0.5

st.markdown("### Simulation Parameters")
n_iter = st.slider("Number of iterations", 0, 1000, 100)

#### Model ####

apps_per_node = n_apps // n_nodes
n_active = int(round(n_apps * apps_active_per_day * hours_active_per_day / 8))
memory = [0,]*n_nodes
all_mem_app_idle = mem_idle + manager_memory_idle + per_node_system_memory / apps_per_node
all_mem_app_active = mem_active + manager_memory_active + per_node_system_memory / apps_per_node
apps_mems = [all_mem_app_idle,]*(n_apps-n_active) + [all_mem_app_active,]*n_active
mem_requests = max_mem / apps_per_node
avg_active_per_node = n_active / n_nodes
avg_idle_per_node = (n_apps - n_active) / n_nodes
min_cores_per_node = math.ceil(avg_idle_per_node * (0.05 + manager_cores_idle) + avg_active_per_node * (1.0 + manager_core_active) + per_node_system_cores)

# partition by number of apps per node
def simulate():
    random.shuffle(apps_mems)
    out_of_mem = False
    for i in range(n_nodes):
        # Is this equivalent to a greedy scheduler?
        node_mems = apps_mems[i*apps_per_node:(i + 1)*apps_per_node]
        total_mem = sum(node_mems)
        if total_mem > max_mem:
            out_of_mem = True
    return out_of_mem


out_of_mem = 0
for _ in range(n_iter):
    out_of_mem += simulate()

#### Output ####

st.markdown("## Model Output")
st.write("Number of active apps:", n_active)
st.write("Avg number of active apps per node:", avg_active_per_node)
st.write("Minimum number of cores per node (suggested):", min_cores_per_node)
st.write("Total CPUs:", min_cores_per_node * n_nodes)
st.write("Memory requests:", mem_requests)
st.write("Packing rate (apps per node):", apps_per_node)
st.markdown("## Executive Metrics")
st.write("Probability that one or more apps are out of memory in the cluster:")
st.write("=>", out_of_mem / n_iter)
st.write("Packing rate (apps per CPU) - compare with current rate of 0.75")
st.write("=>", n_apps / min_cores_per_node / n_nodes)

