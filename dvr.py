# AUTHOR: Subhajit Halder
# DATE: 22/04/2025
# ABOUT: Distance Vector Routing Implementation (This is probably gonna take forever to debug)

import threading as th
import socket as sk
import time as tm
N=['A', 'B', 'C', 'D', 'E']  # Global variables because I don't know where else to put them
INF=999  # Close enough to infinity
BASE=5000 
lk=th.Lock()  # I'll figure this locking thing out eventually...

class Node:
    def __init__(self, nm, nbrs):
        # Each node knows its name, its neighbors, and its DV table (which starts dumb)
        self.nm=nm
        self.nbrs=nbrs  # Let's find, Who I'm directly connected to
        self.dv={n: INF for n in N}  # Everyone is far away until proven otherwise
        self.dv[nm]=0  # Distance to myself is obviously 0 right??
        self.hop={n: None for n in N}  # Hop info to reach others
        for nb, c in nbrs.items():
            self.dv[nb]=c  # Direct neighbor distances
            self.hop[nb]=nb  # Direct neighbors are my next hop to them
        self.sk=None
        self.ch=True  # Change flag — starts True so we send some stuff
        self.last_dv=self.dv.copy()  # We'll need this to compare for debug

    def run_srv(self):       
        try:
            self.sk=sk.socket(sk.AF_INET, sk.SOCK_STREAM)
            prt=BASE+N.index(self.nm) # Spin up the server to listen for neighbor updates (may regret this)
            self.sk.bind(('localhost', prt))
            self.sk.listen(5)
            print(f"[INFO] Node {self.nm} server started on port {prt}")
        except Exception as e:
            print(f"[ERROR] Node {self.nm} could not start server: {e}")
            return
        while True:
            try:
                c, _=self.sk.accept()
                d=c.recv(1024).decode()
                c.close()
                if d:
                    self.upd(d)  # Handle whatever my neighbor just yelled at me
            except Exception as e:
                print(f"[ERROR] Node {self.nm} server crashed: {e}")
                break

    def upd(self, d):
        # Handle update from neighbor. Let the Bellman-Ford chaos begin.
        try:
            sndr, dvstr=d.split(':', 1)
            vals=list(map(int, dvstr.split(',')))
            ndv={N[i]: vals[i] for i in range(len(N))}  # Rebuild neighbor's DV
        except:
            print(f"[ERROR] Node {self.nm} received invalid update format.")
            return

        with lk:
            chg=False
            print(f"\n[UPDATE] Node {self.nm} received a distance vector from Node {sndr}")
            print(f"  Previous DV: {self.dv}")
            for dst in N:
                if dst == self.nm:
                    continue  # Skip myself
                if sndr in self.nbrs:
                    cost=self.nbrs[sndr]+ndv[dst]  # Cost to go through sndr to dst
                    if cost < self.dv[dst]:
                        self.dv[dst]=cost  # Update better path
                        self.hop[dst]=sndr  # Update who I forward to
                        chg=True
            if chg:
                self.ch=True
                print(f"  Updated DV: {self.dv}")
            else:
                print("  No change in DV.")  # Nothing new, nothing to do

    def send(self):
        # Send my DV to neighbors. Pls no crashes
        print(f"[SEND] Node {self.nm} preparing to send DV.")
        print(f"  Current DV: {self.dv}")
        print(f"  Last DV:    {self.last_dv}")
        updated = self.dv != self.last_dv
        print(f"  Status: {'Updated' if updated else 'Same'}")
        self.last_dv = self.dv.copy()  # Save for next comparison

        if not self.ch:
            print(f"[INFO] Node {self.nm} has no changes to report.")
            return

        dvstr=','.join(str(self.dv[n]) for n in N)
        for nb in self.nbrs:
            try:
                s=sk.socket(sk.AF_INET, sk.SOCK_STREAM)
                p=BASE+N.index(nb)
                s.connect(('localhost', p))
                s.send(f"{self.nm}:{dvstr}".encode())
                s.close()
                print(f"[INFO] Node {self.nm} sent update to Node {nb}")
            except Exception as e:
                print(f"[ERROR] Node {self.nm} failed to send to {nb}: {e}")
        self.ch=False  # We’re good this round

def lo_nt(f):
    # Let's load the matrix from file. Or not we make one
    try:
        with open(f, 'r') as ff:
            mtx = []
            for line in ff:
                row = list(map(int, line.strip().split()))
                mtx.append(row)
            if len(mtx) == len(N) and all(len(r) == len(N) for r in mtx):
                return mtx
            else:
                print("[WARNING] Invalid matrix size. Using default topology.")
    except:
        print("[WARNING] Network file could not be read. Using default topology.")
    
    # Fallback matrix — our blessed ring topology
    return [
        [0, 2, 0, 0, 1],
        [2, 0, 5, 0, 0],
        [0, 5, 0, 4, 0],
        [0, 0, 4, 0, 1],
        [1, 0, 0, 1, 0]
    ]

def main():
    print("=== Distance Vector Routing Protocol ===")
    print("Initializing network and nodes...")

    mat=lo_nt("network.txt")  # Load or fake the network
    nds={}  # Our nodes live here

    # Time to spawn all the nodes
    for i, nm in enumerate(N):
        nbs={N[j]: mat[i][j] for j in range(len(N)) if mat[i][j] > 0 and i != j}
        nds[nm]=Node(nm, nbs)

    # Start all the node servers in threads
    for n in nds.values():
        th.Thread(target=n.run_srv, daemon=True).start()

    tm.sleep(1)  # Give them time to wake up

    rnd=0
    done=False

    # Begin the simulation: nodes gossip round by round
    while not done and rnd < 70:
        for nm in N:
            rnd += 1
            print(f"\n--- Round {rnd}: {nm} ---")
            nds[nm].send()
            tm.sleep(0.5)
        done=all(not nd.ch for nd in nds.values())  # Check if we're stable

    print("\n=== Final Distance Vector Tables ===")
    for nm in N:
        nd=nds[nm]
        print(f"\nNode {nm} Routing Table:")
        for dst in N:
            if dst != nm:
                print(f"  Destination: {dst}, Cost: {nd.dv[dst]}, Next Hop: {nd.hop[dst]}")
    print(f"\n[INFO] Network converged in {rnd} rounds.")
    print("Distance vector routing process completed successfully.")

main()
