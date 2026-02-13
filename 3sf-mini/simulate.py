from consensus import (
    State, Vote, Block, Config,
    get_latest_justified_hash, get_fork_choice_head,
    compute_hash
)
from p2p import Staker, P2PNetwork
import random

SLOT_DURATION = 12
NUM_STAKERS = 10
ZERO_HASH = '0'*64

if __name__ == '__main__':
    # Create genesis block and state
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

    # Initialize all stakers with genesis
    for staker in stakers:
        assert staker.head == genesis_hash

    print("=== Simulación 3SF-mini iniciada ===")
    print(f"Validadores: {NUM_STAKERS}")
    print(f"Slot duration: {SLOT_DURATION}s")
    print(f"Latencia: Alta (t<667) → Baja (t≥667)\n")

    # Simulation loop
    for time in range(1000):
        # Deliver messages
        network.time_step()

        # Run staker code
        for staker in stakers:
            staker.tick()

        # Periodic printout
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

    print("\n=== Simulación completada ===")
    # Final summary
    print(f"\n=== Estado Final ===")
    staker0 = stakers[0]
    print(f"Total bloques en cadena: {len(staker0.chain)}")
    print(f"Total votos conocidos: {len(staker0.known_votes)}")
    print(f"Último slot finalizado: {staker0.post_states[staker0.head].latest_finalized_slot}")
    print(f"Último slot justificado: {staker0.post_states[staker0.head].latest_justified_slot}")
