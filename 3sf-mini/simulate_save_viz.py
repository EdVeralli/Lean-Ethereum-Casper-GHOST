from consensus import (
    State, Vote, Block, Config,
    get_latest_justified_hash, get_fork_choice_head,
    compute_hash
)
from p2p import Staker, P2PNetwork
import random
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict
import os

SLOT_DURATION = 12
NUM_STAKERS = 10
ZERO_HASH = '0'*64

def plot_view(staker: Staker, filename: str, title="Staker's View"):
    """Visualiza el árbol de bloques y guarda en archivo"""
    G = nx.DiGraph()
    fig, ax = plt.subplots(figsize=(16, 12))

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
        ([vote.validator_id for vote in staker.known_votes] if staker.known_votes else [0])
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
    node_labels = {}
    for node in G.nodes:
        full_hash = None
        for h in staker.chain.keys():
            if h[:8] == node:
                full_hash = h
                break

        if full_hash:
            slot = staker.chain[full_hash].slot
            node_labels[node] = f"{node}\nS{slot}"

        if node == justified_hash[:8]:
            node_colors.append("#3498db")  # Azul
        elif node == finalized_hash[:8]:
            node_colors.append("#9b59b6")  # Púrpura
        elif node == head_block[:8]:
            node_colors.append("#2ecc71")  # Verde
        else:
            node_colors.append("#ecf0f1")  # Gris claro

    # Dibujar bloques
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800,
                          edgecolors='black', linewidths=2)
    nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=15,
                          edge_color='gray', width=2)
    nx.draw_networkx_labels(G, pos, node_labels, font_size=7, font_weight='bold')

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

        color = "#e67e22"  # Naranja
        nx.draw_networkx_nodes(G, pos, nodelist=[voter_node], node_color=color,
                              node_size=300, edgecolors='black', linewidths=1.5)

        if vote.head[:8] in pos:
            nx.draw_networkx_edges(G, pos, edgelist=[(voter_node, vote.head[:8])],
                                  edge_color=color, style="dashed", arrowsize=10, width=1.5)

        if vote.target[:8] in pos:
            nx.draw_networkx_edges(G, pos, edgelist=[(voter_node, vote.target[:8])],
                                  edge_color="gray", style="dotted", arrowsize=8, width=1)

        nx.draw_networkx_labels(G, pos, {voter_node: f"V{vote.validator_id}"},
                               font_size=6, font_weight='bold')

    # Agregar leyenda
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#2ecc71',
                   markersize=12, label='Head (LMD GHOST)', markeredgecolor='black', markeredgewidth=2),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#3498db',
                   markersize=12, label='Justified (2/3 votos)', markeredgecolor='black', markeredgewidth=2),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#9b59b6',
                   markersize=12, label='Finalized', markeredgecolor='black', markeredgewidth=2),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#e67e22',
                   markersize=10, label='Validator Vote', markeredgecolor='black', markeredgewidth=1.5),
        plt.Line2D([0], [0], linestyle='--', color='#e67e22', linewidth=2, label='Vote for Head'),
        plt.Line2D([0], [0], linestyle=':', color='gray', linewidth=2, label='Vote for Target'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

    # Agregar información de estado
    info_text = (
        f"Total Blocks: {len(staker.chain)}\n"
        f"Total Votes: {len(staker.known_votes)}\n"
        f"Finalized Slot: {staker.post_states[staker.head].latest_finalized_slot}\n"
        f"Justified Slot: {staker.post_states[staker.head].latest_justified_slot}"
    )
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    plt.tight_layout()

    # Guardar
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   📊 Guardado: {filename}")

if __name__ == '__main__':
    # Crear directorio para visualizaciones
    viz_dir = "visualizations"
    os.makedirs(viz_dir, exist_ok=True)

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

    print("=== Simulación 3SF-mini con Visualización Guardada ===")
    print(f"Validadores: {NUM_STAKERS}")
    print(f"Slot duration: {SLOT_DURATION}s")
    print(f"Latencia: Alta (t<667) → Baja (t≥667)")
    print(f"\nGuardando visualizaciones en: ./{viz_dir}/")
    print(f"Frecuencia: cada 60 time units (5 slots)\n")

    # Loop de simulación
    for time in range(1000):
        # Entregar mensajes
        network.time_step()

        # Ejecutar stakers
        for staker in stakers:
            staker.tick()

        # Printout periódico
        if time % SLOT_DURATION == 0:
            current_slot = time // SLOT_DURATION + 2
            print(f"\n=== Time {time} (Slot {current_slot}) ===")
            staker0 = stakers[0]
            head = staker0.head
            ljh, lfh = staker0.latest_justified_hash, staker0.latest_finalized_hash
            if head:
                ljs = staker0.chain[ljh].slot if ljh != ZERO_HASH else 0
                lfs = staker0.chain[lfh].slot if lfh != ZERO_HASH else 0
                print(f"Staker 0: Head={head[:8]} (slot {staker0.chain[head].slot:3d}) | "
                      f"Justified={ljh[:8]} (slot {ljs:3d}) | Finalized={lfh[:8]} (slot {lfs:3d})")

        # Visualizar cada 60 time units (5 slots)
        if time % 60 == 9 and time > 0:
            current_slot = time // SLOT_DURATION + 2
            filename = f"{viz_dir}/block_tree_slot_{current_slot:03d}.png"
            plot_view(stakers[0], filename,
                     f"3SF Block Tree - Slot {current_slot}")

    print("\n=== Simulación completada ===")

    # Estado final
    print(f"\n=== Estado Final ===")
    staker0 = stakers[0]
    print(f"Total bloques en cadena: {len(staker0.chain)}")
    print(f"Total votos conocidos: {len(staker0.known_votes)}")
    print(f"Último slot finalizado: {staker0.post_states[staker0.head].latest_finalized_slot}")
    print(f"Último slot justificado: {staker0.post_states[staker0.head].latest_justified_slot}")

    # Visualización final
    print(f"\n📊 Guardando visualización final...")
    final_slot = staker0.chain[staker0.head].slot
    filename = f"{viz_dir}/block_tree_final_slot_{final_slot}.png"
    plot_view(stakers[0], filename,
             f"3SF Final State - Slot {final_slot}")

    print(f"\n✅ Todas las visualizaciones guardadas en: ./{viz_dir}/")
    print(f"\nPara ver las imágenes:")
    print(f"  open {viz_dir}/")
    print(f"  # o")
    print(f"  ls -lh {viz_dir}/*.png")
