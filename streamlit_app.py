import streamlit as st
import random
import math
from datetime import datetime
random.seed(datetime.now())

import pandas as pd
import numpy as np
import altair as alt

def st_grid(row_headers, column_headers, content):
    elements = st.beta_columns(len(row_headers) + 1)
    index = 0
    for e in elements[1:]:
        e.markdown(row_headers[index])
        index += 1
    index = 0
    for h in column_headers:
        elements = st.beta_columns(len(row_headers) + 1)
        elements[0].markdown(h)
        for e in elements[1:]:
            e.markdown(content[index])
            index += 1

st.title("S4A Probabilistic Cost Reduction Option Model (Option1)")

st.markdown("## Input Parameters")
st.markdown("### Apps Ensemble")
n_apps = st.slider("Total number of apps", 0, 100000, 10000, 100)
apps_active_per_day = st.slider("Fraction of active apps per day", 0.0, 1.0, 0.25, 0.05)
hours_active_per_day = st.slider("Hours an app is active out of the 8 work hours in a day", 0.0, 8.0, 1.0, 0.1)

st.markdown("### App Executor")
col00, col01, col02 = st.beta_columns(3)
col01.markdown("#### CPU")
col02.markdown("#### Memory")

col10, col11, col12 = st.beta_columns(3)
col10.markdown("#### Idle")
mem_idle = col12.slider("", 0.0, 8.0, 0.2, 0.1)
cpu_idle = col11.slider("", 0.0, 8.0, 0.05, 0.05)

col20, col21, col22 = st.beta_columns(3)
col20.markdown("#### Active")
mem_active = col22.slider("", 0.0, 8.0, 2.0, 0.1)
cpu_active = col21.slider("", 0.0, 8.0, 0.5, 0.05)

st.markdown("### Manager")
col00, col01, col02 = st.beta_columns(3)
col01.markdown("#### CPU")
col02.markdown("#### Memory")

col10, col11, col12 = st.beta_columns(3)
col10.markdown("#### Idle")
# Default for idle based on 95p
manager_memory_idle = col12.slider("", 0.0, 1.0, 0.1, 0.1)
manager_cpu_idle = col11.slider("", 0.0, 0.25, 0.05, 0.05)

col20, col21, col22 = st.beta_columns(3)
col20.markdown("#### Active")
# Default for active based on observed max
manager_memory_active = col22.slider("", 0.0, 1.0, 0.5, 0.25)
manager_cpu_active = col21.slider("", 0.0, 1.0, 0.25, 0.25)

st.markdown("### Requests (for Kubernetes scheduler)")
col00, col01, col02 = st.beta_columns(3)
col01.markdown("#### CPU")
col02.markdown("#### Memory")

col10, col11, col12 = st.beta_columns(3)
col10.markdown("#### App Executor")
cpu_requests = col11.slider("", 0.0, 8.0, 0.1, 0.1)
mem_requests = col12.slider("", 0.0, 8.0, 0.8, 0.1)

col20, col21, col22 = st.beta_columns(3)
col20.markdown("#### Manager")
# Default requests for manager based on 2X the 95p
manager_cpu_requests = col21.slider(" ", 0.0, 1.0, 0.1, 0.1)
manager_mem_requests = col22.slider("", 0.0, 1.0, 0.2, 0.1)

st.markdown("### Cluster Nodes Specs")
max_mem = st.slider("Max memory for a node", 1, 64, 16, 1)
max_cpu = st.slider("Max CPU on a node", 1, 64, 4, 1)

st.markdown("### Simulation Parameters")
n_iter = st.slider("Number of iterations", 0, 100, 1)

#### Model ####
# Based on real cluster data
per_node_system_cpu_requests = 1.0
per_node_system_memory_requests = 0.5

# Way conservative estimate
per_node_system_cpu = 0.25
per_node_system_memory = 0.25

class Node():
    def __init__(self):
        self.cpu_requests = per_node_system_cpu_requests
        self.mem_requests = per_node_system_memory_requests
        self.cpu = per_node_system_cpu
        self.mem = per_node_system_memory
    def schedule(self, app):
        if self.cpu_requests + app.cpu_requests <= max_cpu and self.mem_requests + app.mem_requests <= max_mem:
            self.cpu_requests += app.cpu_requests
            self.mem_requests += app.mem_requests
            self.cpu += app.cpu
            self.mem += app.mem
            return True
        return False
    def exceeds_capacity(self):
        return self.mem > max_mem or self.cpu > max_cpu
    def exceeds_cpu(self):
        return self.cpu > max_cpu
    def exceeds_mem(self):
        return self.mem > max_mem
    def __str__(self):
        return f"cpu={self.cpu} mem={self.mem}"

class App():
    def __init__(self):
        # requests
        self.cpu_requests = 0
        self.mem_requests = 0
        self.cpu = 0
        self.mem = 0


#TODO: stacked bar graph of cpu/mem for each app

def draw_nodes(nodes, elements):
    cpus = [(i, 'cpu', n.cpu) for i, n in enumerate(nodes)]
    mems = [(i, 'mem', n.mem) for i, n in enumerate(nodes)]

    #data = cpus + mems

    #df = pd.DataFrame(data, columns=['node', 'type', 'value'])

    df_mem = pd.DataFrame(mems, columns=['node', 'type', 'memory'])
    chart_mem = alt.Chart(df_mem).mark_bar().encode(
        x="node:O",
        y="memory:Q",
        #color=
    )
    line = alt.Chart(pd.DataFrame({'y': [max_mem]})).mark_rule().encode(y='y')
    elements[0].altair_chart(chart_mem + line, use_container_width=True)

    df_cpu = pd.DataFrame(cpus, columns=['node', 'type', 'CPU'])
    chart_cpu = alt.Chart(df_cpu).mark_bar().encode(
        x=alt.X("node:O", axis=alt.Axis(title='Node')),
        y="CPU:Q",
    )
    line = alt.Chart(pd.DataFrame({'y': [max_cpu]})).mark_rule().encode(y='y')
    elements[1].altair_chart(chart_cpu + line, use_container_width=True)
    # TODO: Make two separate charts
    # Highlights when out of capacity
    # Can I better visualize the change in number of nodes?


#apps_per_node = math.ceil(max_mem / mem_requests)
n_active = int(round(n_apps * apps_active_per_day * hours_active_per_day / 8))

apps = []
for i in range(n_active):
    a = App()
    a.cpu_requests = cpu_requests + manager_cpu_requests
    a.mem_requests = mem_requests + manager_mem_requests
    a.cpu = cpu_active + manager_cpu_active
    a.mem = mem_active + manager_memory_active
    apps.append(a)
for i in range(n_apps - n_active):
    a = App()
    a.cpu_requests = cpu_requests + manager_cpu_requests
    a.mem_requests = mem_requests + manager_mem_requests
    a.cpu = cpu_idle + manager_cpu_idle
    a.mem = mem_idle + manager_memory_idle
    apps.append(a)

def schedule(app, nodes):
    i = random.randint(0, len(nodes)-1)
    scheduled = False
    for _ in range(len(nodes)):
        if nodes[i].schedule(app):
            return True
        i = (i + 1) % len(nodes)
    return False

def simulate(elements):
    out_of_mem = 0
    out_of_cpu = 0
    nodes = [Node()]
    random.shuffle(apps)
    for a in apps:
        success = False
        while not success:
            success = schedule(a, nodes)
            if not success:
                nodes.append(Node())
    for n in nodes:
        if n.exceeds_cpu():
            out_of_cpu += 1
        if n.exceeds_mem():
            out_of_mem += 1
    draw_nodes(nodes, elements)
    return out_of_mem, out_of_cpu, len(nodes)


avg_fr_out_of_mem = 0
avg_fr_out_of_cpu = 0
avg_n_nodes = 0
# FIXME: rename
elements = [st.empty(), st.empty()]
for i in range(n_iter):
    out_of_mem, out_of_cpu, n_nodes = simulate(elements)
    #st.markdown(f"#### Simulation #{i}")
    #st.write("Fraction of nodes out of memory:", out_of_mem / n_nodes)
    #st.write("Fraction of nodes out of cpu:", out_of_cpu / n_nodes)
    avg_fr_out_of_mem += out_of_mem / n_nodes
    avg_fr_out_of_cpu += out_of_cpu / n_nodes
    avg_n_nodes += n_nodes
avg_n_nodes /= n_iter
avg_fr_out_of_mem /= n_iter

#### Output ####
st.markdown("## Model Output")
st.write("Number of active apps:", n_active)
#st.write("Avg number of active apps per node:", avg_active_per_node)
#st.write("Minimum number of cpu per node (suggested):", min_cpu_per_node)
#st.write("Total CPUs:", min_cpu_per_node * n_nodes)
#st.write("Memory requests:", mem_requests)
#st.write("Packing rate (apps per node):", apps_per_node)
st.markdown("## Executive Metrics")
st.write("EV of the number of nodes (mean)", avg_n_nodes)
#st.write("Probability that one or more apps is either out of memory or is throttled in the cluster:")
#st.write("=>", out_of_mem / n_iter)
st.write("EV of the fraction of nodes out of memory")
st.write("=>", avg_fr_out_of_mem)
st.write("EV of the fraction of nodes out of cpu")
st.write("=>", avg_fr_out_of_cpu)
st.write("Packing rate (apps per CPU) - compare with current rate of 0.75")
st.write("=>", n_apps / avg_n_nodes / max_cpu)

#TODO: make "memory active" stat decoupled from "core actives"
#TODO: stacked chart with components
#TODO: embellish chart, add max
# TODO: param sweep
