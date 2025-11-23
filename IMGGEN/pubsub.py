import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Vytvorenie priestoru pre diagram
fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor('white')

# Definície farieb pre konzistentnosť
COLOR_BROKER = '#F18F01'
COLOR_PUBLISHER = '#2E86AB'
COLOR_SUBSCRIBER = '#006BA6'
COLOR_PUBLISH_MSG = '#884EA0'
COLOR_SUBSCRIBE_MSG = '#D4AC0D'
COLOR_TITLE = '#2c3e50'
COLOR_TEXT = '#555'

# === MQTT PUBLISH/SUBSCRIBE DIAGRAM ===

G = nx.DiGraph()

# Definícia uzlov
broker_node = "MQTT Broker"
publisher_node = "Publisher\n(Senzor)"
subscriber1_node = "Subscriber 1\n(Aplikácia)"
subscriber2_node = "Subscriber 2\n(Dashboard)"

# Pridanie uzlov
G.add_node(broker_node)
G.add_node(publisher_node)
G.add_node(subscriber1_node)
G.add_node(subscriber2_node)

# Pozície uzlov
pos = {
    publisher_node: (-3, 0),
    broker_node: (0, 0),
    subscriber1_node: (3, 1),
    subscriber2_node: (3, -1),
}

# --- PUBLISH ---
# Publisher posiela správu (PUBLISH) na Broker
G.add_edge(publisher_node, broker_node, key="publish", label="PUBLISH: /dom/teplota")

# --- SUBSCRIBE ---
# Subscribere sa prihlásia na tému (SUBSCRIBE) na Brokeri
G.add_edge(broker_node, subscriber1_node, key="sub1", label="SUBSCRIBE: /dom/teplota")
G.add_edge(broker_node, subscriber2_node, key="sub2", label="SUBSCRIBE: /dom/teplota")

# --- DRAWING ---
ax.set_title("Princíp MQTT Publish/Subscribe",
              fontsize=18, fontweight='bold', pad=20, color=COLOR_TITLE)

# Uzly
nx.draw_networkx_nodes(G, pos, nodelist=[broker_node], node_color=COLOR_BROKER,
                       node_size=4500, node_shape='s', ax=ax,
                       edgecolors=COLOR_BROKER, linewidths=3)
nx.draw_networkx_nodes(G, pos, nodelist=[publisher_node], node_color=COLOR_PUBLISHER,
                       node_size=3500, node_shape='s', ax=ax,
                       edgecolors='#1a5276', linewidths=3)
nx.draw_networkx_nodes(G, pos, nodelist=[subscriber1_node, subscriber2_node], node_color=COLOR_SUBSCRIBER,
                       node_size=3000, ax=ax,
                       edgecolors='#004a73', linewidths=2.5)

# Popisky uzlov
nx.draw_networkx_labels(G, pos, font_size=11, font_weight='bold', ax=ax)

# Hrany pre PUBLISH
nx.draw_networkx_edges(G, pos, edgelist=[(publisher_node, broker_node)],
                       arrows=True, arrowstyle='-|>',
                       width=3, edge_color=COLOR_PUBLISH_MSG, ax=ax,
                       arrowsize=20, connectionstyle='arc3,rad=0.1')
ax.text(-1.5, 0.3, "1. PUBLISH (Téma: /dom/teplota)\nSpráva: {\"temp\": 23.5}",
        ha='center', fontsize=10, color=COLOR_PUBLISH_MSG) # Odstránené font_weight


# Hrany pre SUBSCRIBE a Delivery
nx.draw_networkx_edges(G, pos, edgelist=[(broker_node, subscriber1_node)],
                       arrows=True, arrowstyle='-|>',
                       width=3, edge_color=COLOR_SUBSCRIBE_MSG, ax=ax,
                       arrowsize=20, connectionstyle='arc3,rad=-0.1')
ax.text(1.5, 0.7, "2. SUBSCRIBE (Téma: /dom/teplota)\n3. DELIVERY",
        ha='center', fontsize=10, color=COLOR_SUBSCRIBE_MSG) # Odstránené font_weight

nx.draw_networkx_edges(G, pos, edgelist=[(broker_node, subscriber2_node)],
                       arrows=True, arrowstyle='-|>',
                       width=3, edge_color=COLOR_SUBSCRIBE_MSG, ax=ax,
                       arrowsize=20, connectionstyle='arc3,rad=0.1')
ax.text(1.5, -0.7, "2. SUBSCRIBE (Téma: /dom/teplota)\n3. DELIVERY",
        ha='center', fontsize=10, color=COLOR_SUBSCRIBE_MSG) # Odstránené font_weight

# Popisky krokov pre lepšie pochopenie
ax.text(0, -2.5,
        "1. Publisher (napr. senzor) odošle správu na tému (`/dom/teplota`) k MQTT Brokerovi.\n"
        "2. Subscribere (napr. aplikácie) sa prihlásia na odber konkrétnych tém u brokera.\n"
        "3. Broker doručí správu všetkým prihláseným Subscriberom na danú tému.",
        ha='center', fontsize=11, color=COLOR_TEXT, bbox=dict(facecolor='lightgrey', alpha=0.2, edgecolor='none'))

ax.axis('off')
ax.set_xlim(-4.5, 4.5)
ax.set_ylim(-3.5, 2.5)

# --- Legenda ---
legend_elements = [
    mpatches.Patch(facecolor=COLOR_PUBLISHER, edgecolor='#1a5276', label='Publisher (Odosielateľ)', linewidth=2),
    mpatches.Patch(facecolor=COLOR_BROKER, edgecolor=COLOR_BROKER, label='MQTT Broker (Sprostredkovateľ)', linewidth=2),
    mpatches.Patch(facecolor=COLOR_SUBSCRIBER, edgecolor='#004a73', label='Subscriber (Príjemca)', linewidth=2),
    mpatches.Patch(facecolor=COLOR_PUBLISH_MSG, label='PUBLISH (Odoslanie správy)', linewidth=2),
    mpatches.Patch(facecolor=COLOR_SUBSCRIBE_MSG, label='SUBSCRIBE / DELIVERY (Prihlásenie / Doručenie)', linewidth=2)
]
fig.legend(handles=legend_elements, loc='lower center', ncol=3,
           frameon=True, fontsize=11, bbox_to_anchor=(0.5, -0.07))

plt.tight_layout(rect=[0, 0.1, 1, 1]) # Upravíme layout, aby legenda neprekrývala text
plt.savefig('mqtt_publish_subscribe_concept.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.show()