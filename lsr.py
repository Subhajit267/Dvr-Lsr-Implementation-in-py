# AUTHOR: Subhajit Halder
# DATE: 22/04/2025
# ABOUT: Link State Routing Implementation (Dijkstra's algorithm))

import threading as th
import socket as sk
import heapq as hq
from collections import defaultdict as dd
import time as tm

# Global stuff - because globals are evil but convenient
N = ['A', 'B', 'C', 'D', 'E']  # Our beloved nodes
INF = 999999  # Close enough to infinity for my work
BASE_PORT = 6000  # Different from DVR ports, because...why not

# The all-knowing LSDB (Link State Database)
lsdb = dd(dict)
db_lock = th.Lock()  # Pray this prevents race conditions

round_count = 0  # Track how many rounds till convergence

class LSNode:
    def __init__(self, name, nbrs):
        self.name = name  # Who am I
        self.nbrs = nbrs  # Who I know (direct links)
        self.seq = 0  # Sequence number so people know when I speak again
        self.sock = None
        self.done = False  # Flag for ending this endless thread life
        self.received = {}  # Keep track of latest messages from others

        # Dump my neighbor info into LSDB — the gossip starts here
        with db_lock:
            for nb, cost in nbrs.items():
                lsdb[self.name][nb] = cost

    def run_srv(self):        
        try:
            self.sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
            self.sock.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)# Spin up a TCP server so friends can talk to me
            port = BASE_PORT + N.index(self.name)
            self.sock.bind(('localhost', port))
            self.sock.listen(5)
            print(f"[INFO] Node {self.name} server ready on port {port}") 
        except Exception as e:
            print(f"[ERROR] Node {self.name} server died: {e}")#Alas, task failed
            return

        while not self.done:
            try:
                c, _ = self.sock.accept()
                d = c.recv(1024).decode()
                c.close()
                if d:
                    self.handle_lsa(d)
            except Exception as e:  #Failures need to be addressed also
                print(f"[ERROR] Node {self.name} server crashed: {e}")
                break

    def handle_lsa(self, data):
        # Handle the LSA — aka incoming gossip
        try:
            sender, lsa = data.split(':', 1)
            header, info = lsa.split('|', 1)
            src, seq = header.split(',')
            seq = int(seq)
            updates = [u.split(',') for u in info.split(';') if u]
        except:
            print(f"[ERROR] Node {self.name} got garbage LSA. Ignored.")
            return

        with db_lock:
            # If it's old gossip, ignore
            if src in self.received and seq <= self.received[src]:
                return
            self.received[src] = seq
            changed = False

            # Check and update my LSDB if I learned anything new
            for s, d, c in updates:
                c = int(c)
                if d not in lsdb[s] or lsdb[s][d] != c:
                    lsdb[s][d] = c
                    changed = True

            if changed:
                print(f"\n[UPDATE] Node {self.name} updated LSDB from {sender}:")
                self.print_db()
                self.flood_lsa(sender, lsa)  # Forward the gossip

    def flood_lsa(self, sender, lsa_data):
        # Let's flood the LSA to everyone else (but not the one who told me)
        for nb in self.nbrs:
            if nb == sender:
                continue
            try:
                s = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
                port = BASE_PORT + N.index(nb)
                s.connect(('localhost', port))
                s.send(f"{self.name}:{lsa_data}".encode())
                s.close()
                print(f"[INFO] Node {self.name} flooded LSA to Node {nb}")
            except Exception as e:
                print(f"[ERROR] Node {self.name} failed to flood to {nb}: {e}")

    def send_lsa(self):
        # Brag about my links to everyone nearby
        self.seq += 1
        lsa_parts = [f"{self.name},{nb},{cost}" for nb, cost in self.nbrs.items()]
        msg = f"{self.name},{self.seq}|{';'.join(lsa_parts)}"

        for nb in self.nbrs:
            try:
                s = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
                port = BASE_PORT + N.index(nb)
                s.connect(('localhost', port))
                s.send(f"{self.name}:{msg}".encode())
                s.close()
                print(f"[INFO] Node {self.name} sent initial LSA to Node {nb}")
            except Exception as e:
                print(f"[ERROR] Node {self.name} failed to LSA {nb}: {e}")

    def print_db(self):
        # Just showing off the current LSDB state
        print("  Current LSDB:")
        for src in lsdb:
            print(f"    {src}: {dict(lsdb[src])}")

def dijkstra(start):
    # Our savior: Dijkstra’s shortest path magic
    dist = {n: INF for n in N}
    dist[start] = 0
    prev = {n: None for n in N}
    q = [(0, start)]

    while q:
        d, u = hq.heappop(q)
        if d > dist[u]:
            continue
        for v, c in lsdb.get(u, {}).items():
            alt = d + c
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                hq.heappush(q, (alt, v))
    return dist

def load_net():
    # trying to read the topology or fake it (or even better make it)
    try:
        with open('network.txt', 'r') as f:
            mat = [list(map(int, line.split())) for line in f]
            if len(mat) == 5 and all(len(row) == 5 for row in mat):
                print("[INFO] Network loaded from file")
                return mat
            else:
                print("[WARNING] Invalid network. Falling back")
    except:
        print("[WARNING] No file. Falling back.")

    # Default topology — the blessed ring
    return [
        [0, 2, 0, 0, 1],
        [2, 0, 5, 0, 0],
        [0, 5, 0, 4, 0],
        [0, 0, 4, 0, 1],
        [1, 0, 0, 1, 0]
    ]

def main():
    global round_count
    print("\n=== Link State Routing Protocol ===")  # let's print the program name
    print("Building the world...")
    mat = load_net()

    # Set up the universe (i.e., nodes)
    nodes = {}
    for i, name in enumerate(N):
        nbrs = {N[j]: mat[i][j] for j in range(len(N)) if mat[i][j] > 0 and i != j}
        nodes[name] = LSNode(name, nbrs)

    # Fire up all servers (they’re shy, so do it quietly)
    for node in nodes.values():
        th.Thread(target=node.run_srv, daemon=True).start()

    tm.sleep(1)  # Give servers time to wake up
    print("\n=== LSA FLOOD BEGINS ===")

    # Everyone yells their link state info
    for node in nodes.values():
        node.send_lsa()

    tm.sleep(3)  # Time for the LSA to make rounds
    for node in nodes.values():
        node.done = True  # Tell everyone to chill

    round_count = 1  # Only one real round of flooding here

    print("\n=== FINAL ROUTING TABLES ===")
    with db_lock:
        for node in N:
            print(f"\nRouting table for Node {node}:")
            paths = dijkstra(node)
            for dst in N:
                if dst != node:
                    print(f"  To {dst}: Cost = {paths[dst]}")

    print(f"\n[INFO] LSR converged in {round_count} rounds.")
    print("[INFO] LSR routing process done.")

main()
