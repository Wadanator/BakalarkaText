import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.patch.set_facecolor('white')

# === PRIAMA TOPOLÓGIA ===
G1 = nx.DiGraph()
main = "Main\nController"
hw1 = ["HW 1", "HW 2", "HW 3", "HW 4", "HW 5", "HW 6"]

for hw in hw1:
    G1.add_edge(main, hw)

# Pozície - radiálne rozloženie
pos1 = {main: (0, 0)}
import math
n = len(hw1)
radius = 2.5
for i, hw in enumerate(hw1):
    angle = 2 * math.pi * i / n - math.pi/2
    pos1[hw] = (radius * math.cos(angle), radius * math.sin(angle))

ax1 = axes[0]
# Main controller
nx.draw_networkx_nodes(G1, pos1, nodelist=[main], node_color='#2E86AB', 
                       node_size=3500, node_shape='s', ax=ax1, 
                       edgecolors='#1a5276', linewidths=3)
# HW zariadenia
nx.draw_networkx_nodes(G1, pos1, nodelist=hw1, node_color='#A23B72', 
                       node_size=1800, ax=ax1, 
                       edgecolors='#6b1f47', linewidths=2.5)
# Hrany
nx.draw_networkx_edges(G1, pos1, arrows=True, arrowstyle='-|>', 
                       width=2.5, edge_color='#34495e', ax=ax1, 
                       arrowsize=20, connectionstyle='arc3,rad=0.1')
# Popisky
nx.draw_networkx_labels(G1, pos1, font_size=11, font_weight='bold', 
                        font_family='sans-serif', ax=ax1)

ax1.set_title("Priama topológia", fontsize=16, fontweight='bold', 
              pad=20, color='#2c3e50')
ax1.text(0.5, -0.05, "Centralizované riadenie", transform=ax1.transAxes,
         ha='center', fontsize=11, style='italic', color='#555')
ax1.axis('off')
ax1.set_xlim(-3.5, 3.5)
ax1.set_ylim(-3.5, 3.5)

# === HIERARCHICKÁ TOPOLÓGIA ===
G2 = nx.DiGraph()
master = "Master\nController"
slaves = ["Slave 1", "Slave 2", "Slave 3", "Slave 4"]
hw_map = {
    "Slave 1": ["HW 1", "HW 2"],
    "Slave 2": ["HW 3", "HW 4"],
    "Slave 3": ["HW 5", "HW 6"],
    "Slave 4": ["HW 7", "HW 8"]
}

for s in slaves:
    G2.add_edge(master, s)
    for hw in hw_map[s]:
        G2.add_edge(s, hw)

# Pozície - stromová hierarchia
pos2 = {
    master: (0, 3),
    "Slave 1": (-3, 1.2),
    "Slave 2": (-1, 1.2),
    "Slave 3": (1, 1.2),
    "Slave 4": (3, 1.2),
}

hw_positions = [
    [(-3.5, -0.5), (-2.5, -0.5)],
    [(-1.5, -0.5), (-0.5, -0.5)],
    [(0.5, -0.5), (1.5, -0.5)],
    [(2.5, -0.5), (3.5, -0.5)]
]

for i, (slave, hw_list) in enumerate(hw_map.items()):
    for j, hw in enumerate(hw_list):
        pos2[hw] = hw_positions[i][j]

ax2 = axes[1]
all_hw = [hw for hwlist in hw_map.values() for hw in hwlist]

# Master
nx.draw_networkx_nodes(G2, pos2, nodelist=[master], node_color='#F18F01', 
                       node_size=3500, node_shape='s', ax=ax2,
                       edgecolors='#c46f01', linewidths=3)
# Slaves
nx.draw_networkx_nodes(G2, pos2, nodelist=slaves, node_color='#006BA6', 
                       node_size=2200, ax=ax2,
                       edgecolors='#004a73', linewidths=2.5)
# HW
nx.draw_networkx_nodes(G2, pos2, nodelist=all_hw, node_color='#A23B72', 
                       node_size=1400, ax=ax2,
                       edgecolors='#6b1f47', linewidths=2.5)
# Hrany
nx.draw_networkx_edges(G2, pos2, arrows=True, arrowstyle='-|>', 
                       width=2.5, edge_color='#34495e', ax=ax2,
                       arrowsize=20, connectionstyle='arc3,rad=0.1')
# Popisky
nx.draw_networkx_labels(G2, pos2, font_size=11, font_weight='bold',
                        font_family='sans-serif', ax=ax2)

ax2.set_title("Hierarchická topológia", fontsize=16, fontweight='bold',
              pad=20, color='#2c3e50')
ax2.text(0.5, -0.05, "Distribuované riadenie", transform=ax2.transAxes,
         ha='center', fontsize=11, style='italic', color='#555')
ax2.axis('off')
ax2.set_xlim(-4.5, 4.5)
ax2.set_ylim(-1.5, 4)

# Legenda
legend_elements = [
    mpatches.Patch(facecolor='#2E86AB', edgecolor='#1a5276', 
                   label='Main Controller', linewidth=2),
    mpatches.Patch(facecolor='#F18F01', edgecolor='#c46f01', 
                   label='Master Controller', linewidth=2),
    mpatches.Patch(facecolor='#006BA6', edgecolor='#004a73', 
                   label='Slave Controller', linewidth=2),
    mpatches.Patch(facecolor='#A23B72', edgecolor='#6b1f47', 
                   label='HW zariadenie', linewidth=2)
]
fig.legend(handles=legend_elements, loc='lower center', ncol=4, 
           frameon=True, fontsize=11, bbox_to_anchor=(0.5, -0.02))

plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig('topologie_network.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.show()