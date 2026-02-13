from consensus import (
    State, Vote, Block, Config,
    get_latest_justified_hash, get_fork_choice_head,
    compute_hash
)
from p2p import Staker, P2PNetwork
import random
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict

SLOT_DURATION = 12
NUM_STAKERS = 10
ZERO_HASH = '0'*64

def plot_view(fig, ax, staker: Staker, title="Staker's View"):
    """Visualiza el árbol de bloques del validador"""
    G = nx.DiGraph()
    plt.clf()

    # Construir estructura del grafo
    children_map = defaultdict(list)
    for block in staker.chain.values():
        h = compute_hash(block)
        if block.parent != ZERO_HASH:
            children_map[block.parent].append(h)
        G.add_node(h[:8], slot=block.slot)

    for parent, children in children_map.items():
        for child in children:
            G.add_edge(parent[:8], child[:8])

    # DFS para asignar posiciones x consistentes
    pos = {}
    x_counter = [0]
    max_validator_id = max(
        [staker.validator_id] +
        [vote.validator_id for vote in staker.known_votes]
    )

    def dfs(block_hash, depth=0):
        if block_hash not in children_map:
            x = x_counter[0]
            x_counter[0] += 1
            pos[block_hash[:8]] = (x, -staker.chain[block_hash].slot)
            return x
        child_xs = []
        for child in sorted(children_map[block_hash]):
            child_xs.append(dfs(child))
        x = sum(child_xs) / len(child_xs)
        pos[block_hash[:8]] = (x, -staker.chain[block_hash].slot)
        return x

    # Comenzar DFS desde genesis
    dfs(staker.genesis_hash)

    # Colorear bloques según estado
    justified_hash = get_latest_justified_hash(staker.post_states)
    finalized_hash = staker.latest_finalized_hash
    head_block = get_fork_choice_head(staker.chain, justified_hash, staker.known_votes)

    node_colors = []
    for node in G.nodes:
        if node == justified_hash[:8]:
            node_colors.append("blue")
        elif node == finalized_hash[:8]:
            node_colors.append("purple")
        elif node == head_block[:8]:
            node_colors.append("green")
        else:
            node_colors.append("lightgray")

    # Dibujar bloques
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=600)
    nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=10)
    nx.draw_networkx_labels(G, pos, font_size=8)

    # Dibujar votos
    latest_votes = {}
    for vote in sorted(staker.known_votes, key=lambda vote: vote.slot):
        latest_votes[vote.validator_id] = vote

    for vote in latest_votes.values():
        if vote.head[:8] not in pos:
            continue
        voter_node = f"v{vote.validator_id}"
        offset = (vote.validator_id - max_validator_id / 2) * 0.15
        pos[voter_node] = (pos[vote.head[:8]][0] + offset, pos[vote.head[:8]][1] - 0.5)

        G.add_node(voter_node, node_size=5)
        G.add_edge(voter_node, vote.head[:8])
        G.add_edge(voter_node, vote.target[:8])

        color = "orange"
        nx.draw_networkx_nodes(G, pos, nodelist=[voter_node], node_color=color, node_size=200)
        nx.draw_networkx_edges(G, pos, edgelist=[(voter_node, vote.head[:8])], edge_color=color,
                               style="dashed", arrowsize=8)
        nx.draw_networkx_edges(G, pos, edgelist=[(voter_node, vote.target[:8])], edge_color="grey",
                               style="dashed", arrowsize=8)
        nx.draw_networkx_labels(G, pos, labels={voter_node: f"v{vote.validator_id}"}, font_size=6)

    # Agregar leyenda
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green',
                   markersize=10, label='Head'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue',
                   markersize=10, label='Justified'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='purple',
                   markersize=10, label='Finalized'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange',
                   markersize=8, label='Voter'),
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    ax.set_title(title)
    ax.axis('off')
    fig.tight_layout()
    fig.canvas.draw()
    fig.canvas.flush_events()

if __name__ == '__main__':
    # Configurar matplotlib para modo interactivo
    plt.ion()
    fig, ax = plt.subplots(figsize=(14, 10))
    plt.show(block=False)

    # Crear genesis block y state
    genesis_block = Block(slot=1, parent=ZERO_HASH)
    genesis_state = State(
        latest_finalized_hash=ZERO_HASH,
        latest_finalized_slot=0,
        latest_justified_hash=ZERO_HASH,
        latest_justified_slot=0,
        historical_block_hashes=[ZERO_HASH],
        justified_slots=[True],
        config=Config(num_validators=NUM_STAKERS)
    )
    genesis_block.state_root = compute_hash(genesis_state)
    genesis_hash = compute_hash(genesis_block)

    def latency_func(t):
        if t < 667:
            return int(SLOT_DURATION * 2.5 * random.random() ** 3)
        else:
            return 1

    network = P2PNetwork(latency_func)
    stakers = [Staker(i, network, genesis_block, genesis_state) for i in range(NUM_STAKERS)]

    # Verificar inicialización
    for staker in stakers:
        assert staker.head == genesis_hash

    print("=== Simulación 3SF-mini con Visualización ===")
    print(f"Validadores: {NUM_STAKERS}")
    print(f"Slot duration: {SLOT_DURATION}s")
    print(f"Latencia: Alta (t<667) → Baja (t≥667)")
    print(f"\nVisualizando árbol de bloques cada 60 time units...")
    print(f"Colores: Verde=Head, Azul=Justified, Púrpura=Finalized")
    print(f"         Naranja=Votantes\n")

    # Loop de simulación
    for time in range(1000):
        # Entregar mensajes
        network.time_step()

        # Ejecutar stakers
        for staker in stakers:
            staker.tick()

        # Printout periódico
        if time % SLOT_DURATION == 0:
            print(f"\n=== Time {time} (Slot {time // SLOT_DURATION + 2}) ===")
            for staker in stakers:
                head = staker.head
                ljh, lfh = staker.latest_justified_hash, staker.latest_finalized_hash
                if head:
                    ljs = staker.chain[ljh].slot if ljh != ZERO_HASH else 0
                    lfs = staker.chain[lfh].slot if lfh != ZERO_HASH else 0
                    print(f"Staker {staker.validator_id}: Head={head[:8]} (slot {staker.chain[head].slot:3d}) | "
                          f"Justified={ljh[:8]} (slot {ljs:3d}) | Finalized={lfh[:8]} (slot {lfs:3d})")

        # Visualizar cada 60 time units (5 slots)
        if time % 60 == 9:
            current_slot = time // SLOT_DURATION + 2
            print(f"\n📊 Visualizando árbol de bloques (Slot {current_slot})...")
            plot_view(fig, ax, stakers[0], f"Staker 0 - Slot {current_slot}")
            plt.pause(0.1)

    print("\n=== Simulación completada ===")

    # Estado final
    print(f"\n=== Estado Final ===")
    staker0 = stakers[0]
    print(f"Total bloques en cadena: {len(staker0.chain)}")
    print(f"Total votos conocidos: {len(staker0.known_votes)}")
    print(f"Último slot finalizado: {staker0.post_states[staker0.head].latest_finalized_slot}")
    print(f"Último slot justificado: {staker0.post_states[staker0.head].latest_justified_slot}")

    # Visualización final
    print("\n📊 Mostrando visualización final del árbol de bloques...")
    print("   Cierra la ventana para terminar el programa.")
    plot_view(fig, ax, stakers[0], f"Estado Final - Slot {staker0.chain[staker0.head].slot}")
    plt.ioff()
    plt.show()  # Bloquea hasta que se cierre la ventana
