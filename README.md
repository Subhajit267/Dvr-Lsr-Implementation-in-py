# Network Routing Protocols Implementation

Implementation of Distance Vector Routing (DVR) and Link State Routing (LSR) protocols in Python.

## 📋 Table of Contents

* [Overview](#-overview)
* [Features](#-features)
* [Protocols Implemented](#-protocols-implemented)
* [Installation](#-installation)
* [Usage](#-usage)
* [Network Topology](#-network-topology)
* [Code Structure](#-code-structure)
* [Output Analysis](#-output-analysis)
* [Technical Details](#-technical-details)
* [Troubleshooting](#-troubleshooting)
* [Performance Notes](#-performance-notes)
* [Future Enhancements](#-future-enhancements)
* [Developer](#-developer)
* [License](#-license)
* [Contributing](#-contributing)
* [Support](#-support)

## 🚀 Overview

This project implements two fundamental network routing protocols:

* **Distance Vector Routing (DVR)** - Using Bellman-Ford algorithm
* **Link State Routing (LSR)** - Using Dijkstra's algorithm

Both protocols are implemented in Python with socket programming for inter-node communication and threading for concurrent node operations.

## ✨ Features

### 🔄 Distance Vector Routing (DVR)

* Bellman-Ford Algorithm for path calculation
* Incremental updates between neighbors
* Routing table convergence detection
* Multi-threaded node communication
* Change tracking and update optimization

### 🌐 Link State Routing (LSR)

* Dijkstra's Algorithm for shortest path calculation
* Link State Advertisement (LSA) flooding
* Sequence number tracking to prevent loops
* Global topology database maintenance
* Efficient flooding mechanism

### 🎯 Common Features

* 5-Node network topology (A, B, C, D, E)
* Configurable network costs
* Real-time protocol simulation
* Detailed logging and debugging
* Convergence time measurement

## 📊 Protocols Implemented

### Distance Vector Routing (`dvr.py`)

* Algorithm: Bellman-Ford
* Each node maintains distance vector to all destinations
* Periodic updates to neighbors
* Convergence when no changes occur
* Handles network changes dynamically

### Link State Routing (`lsr.py`)

* Algorithm: Dijkstra's
* Each node floods link state information
* All nodes build identical topology maps
* Calculates shortest paths independently
* Faster convergence than DVR

## 📥 Installation

### Prerequisites

* Python 3.6 or higher
* No external dependencies (standard library only)

### Quick Setup

```bash
# Clone or download the project files
# Ensure you have both files in the same directory:
# - dvr.py (Distance Vector Routing)
# - lsr.py (Link State Routing)
```

## 🚀 Usage

### Running Distance Vector Routing

```bash
python dvr.py
```

### Running Link State Routing

```bash
python lsr.py
```

### Using Custom Network Topology

* Create a file named `network.txt`
* Add your 5x5 adjacency matrix, e.g.:

```
0 2 0 0 1
2 0 5 0 0
0 5 0 4 0
0 0 4 0 1
1 0 0 1 0
```

* Run either protocol; it will automatically detect the file

## 🌐 Network Topology

**Default Topology (Ring Network)**

```
    A---2---B
    |       |
    1       5
    |       |
    E---1---C
            |
            4
            |
            D
```

**Node Configuration**

* Nodes: A, B, C, D, E
* Port Range: 5000-5004 (DVR), 6000-6004 (LSR)
* Infinity Value: 999 (DVR), 999999 (LSR)

## 📁 Code Structure

### Distance Vector Routing (`dvr.py`)

```
dvr.py
├── Global Variables
│   ├── N = ['A', 'B', 'C', 'D', 'E']
│   ├── INF = 999
│   └── BASE_PORT = 5000
├── Node Class
│   ├── __init__() - Initialize routing table
│   ├── run_srv() - TCP server for updates
│   ├── upd() - Process received distance vectors
│   └── send() - Broadcast updates to neighbors
└── Main Function
    ├── load_network() - Read topology file
    └── Simulation loop until convergence
```

### Link State Routing (`lsr.py`)

```
lsr.py
├── Global Variables
│   ├── N = ['A', 'B', 'C', 'D', 'E']
│   ├── INF = 999999
│   └── BASE_PORT = 6000
├── LSNode Class
│   ├── __init__() - Initialize node and LSDB
│   ├── run_srv() - TCP server for LSAs
│   ├── handle_lsa() - Process received LSAs
│   ├── flood_lsa() - Forward LSAs to neighbors
│   └── send_lsa() - Broadcast own link state
├── dijkstra() - Shortest path calculation
└── Main Function
    ├── load_network() - Read topology file
    └── LSA flooding and routing table calculation
```

## 📊 Output Analysis

### DVR Expected Output

```
=== Distance Vector Routing Protocol ===
Initializing network and nodes...
[INFO] Node A server started on port 5000
...
[UPDATE] Node A received a distance vector from Node B
  Previous DV: {'A': 0, 'B': 2, 'C': 999, 'D': 999, 'E': 1}
  Updated DV: {'A': 0, 'B': 2, 'C': 7, 'D': 999, 'E': 1}

=== Final Distance Vector Tables ===
Node A Routing Table:
  Destination: B, Cost: 2, Next Hop: B
  Destination: C, Cost: 7, Next Hop: B
...
[INFO] Network converged in 12 rounds.
```

### LSR Expected Output

```
=== Link State Routing Protocol ===
Building the world...
[INFO] Node A server ready on port 6000
...
[UPDATE] Node A updated LSDB from B:
  Current LSDB:
    A: {'B': 2, 'E': 1}
    B: {'A': 2, 'C': 5}
    ...
=== FINAL ROUTING TABLES ===
Routing table for Node A:
  To B: Cost = 2
  To C: Cost = 7
  ...
[INFO] LSR converged in 1 rounds.
```

## 🔧 Technical Details

* **Communication Protocol:** TCP sockets for reliable message delivery
* **Custom message formats:** DVR and LSR updates
* **Thread-safe operations:** locking mechanisms

**DVR Update Format:**

```
Sender:DV_Values
Example: "A:0,2,999,999,1"
```

**LSA Message Format:**

```
Sender:Source,Sequence|Updates
Example: "A:A,1|A,B,2;A,E,1"
```

**Convergence Characteristics:**

| Protocol | Convergence Time | Message Complexity | Memory Usage |
| -------- | ---------------- | ------------------ | ------------ |
| DVR      | 10-15 rounds     | O(n) per node      | Lower        |
| LSR      | 1-2 rounds       | O(n²) initially    | Higher       |

## 🐛 Troubleshooting

* **Address already in use:** Wait a few seconds or check port ranges
* **No network.txt file:** Program uses default ring topology
* **Socket connection errors:** Check firewall and port availability
* **Debugging Tips:** Enable detailed logging, verify individual node startup, monitor updates

## 🚀 Performance Notes

* **DVR Advantages:** Simple, low memory, incremental updates, suitable for small networks
* **LSR Advantages:** Faster convergence, loop prevention, better for larger networks, accurate routing

## 📈 Future Enhancements

* Network change simulation
* Graphical visualization
* Performance metrics collection
* Support for larger networks
* Dynamic topology changes
* Route poisoning, split horizon, OSPF-like areas, QoS metrics

## 👨‍💻 Developer

* Subhajit Halder
* Date: April 22, 2025
* Email: subhajithalder267@outlook.com
* About: Educational network protocols implementation

## 📄 License

* Educational and research purposes
* Modify and distribute with proper attribution

## 🤝 Contributing

* Code optimization
* Additional features
* Documentation improvements
* Testing and validation

*Last Updated: April 2025 | Python 3.6+*

## 📞 Support

* Check troubleshooting section
* Verify Python version compatibility
* Ensure network.txt format is correct
* Review console output for errors

Happy Networking! 🌐
