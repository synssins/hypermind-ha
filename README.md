# Hypermind Home Assistant Integration

[\![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[\![GitHub Release](https://img.shields.io/github/release/synssins/hypermind-ha.svg)](https://github.com/synssins/hypermind-ha/releases)
[\![License](https://img.shields.io/github/license/synssins/hypermind-ha.svg)](LICENSE)

A Home Assistant custom integration for monitoring [Hypermind](https://github.com/lklynet/hypermind) - the decentralized P2P deployment counter.

## What is Hypermind?

Hypermind is a completely decentralized, peer-to-peer deployment counter that tells you how many other people are running the same container. It is The High-Availability Solution to a Problem That Does Not Exist - a fun homelab project that makes a number go up on a screen.

## Features

- **Active Nodes Sensor**: Shows the total number of Hypermind instances running worldwide
- **Direct Connections Sensor**: Shows how many peers your node is directly connected to
- **UI Configuration**: Easy setup via Home Assistant Integrations page
- **Real-time Updates**: Polls the Hypermind API every 5 seconds

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu > **Custom repositories**
3. Add https://github.com/synssins/hypermind-ha with category **Integration**
4. Click **Install**
5. Restart Home Assistant

### Manual Installation

1. Download the latest release from GitHub
2. Copy the custom_components/hypermind folder to your Home Assistant config/custom_components/ directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices and Services** > **Add Integration**
2. Search for Hypermind
3. Enter your Hypermind host and port (e.g., 192.168.1.150 and 3000)

## Sensors

| Entity | Description |
|--------|-------------|
| sensor.hypermind_active_nodes | Total active Hypermind nodes in the swarm |
| sensor.hypermind_direct_connections | Direct P2P connections to your node |

---

## Automation Examples

### 1. RGBW Light Color by Node Count

Control an RGBW light that changes from green (low nodes) to red (high nodes).

### 2. Milestone Announcements via TTS

Announce when the swarm reaches milestone numbers (1000, 5000, 10000 nodes).

### 3. Push Notification on Swarm Growth

Get notified on your phone when the network grows significantly.

### 4. Binary Sensor - Is Swarm Healthy?

Create a binary sensor that indicates if the swarm is online.

### 5. Dashboard Gauge Card

Display the node count as a visual gauge.

### 6. Track Your Connection Health

Monitor if your node has enough direct connections.

### 7. Daily Statistics Log

Log the node count at midnight for historical tracking.

### 8. LED Strip Visualization (WLED)

Create a swarm meter on a WLED strip.

See the full README on GitHub for complete YAML examples.

---

## Use Cases

- **Homelab Dashboard**: Display your contribution to the decentralized swarm
- **Ambient Status Indicator**: Dedicate an RGB bulb to visualize network health
- **Nerd Cred Notifications**: Get push notifications when milestones are reached
- **Connectivity Monitoring**: Ensure your node is well-connected to the P2P network

---

## Running Hypermind

docker run -d --name hypermind --network host --restart unless-stopped -e PORT=3000 ghcr.io/lklynet/hypermind:latest

Important: Use --network host for P2P connectivity to work properly.

## Troubleshooting

### Cannot Connect Error

- Verify Hypermind is running: curl http://YOUR_IP:PORT/api/stats
- Check firewall rules allow access on the port
- Ensure Hypermind is running with --network host in Docker

## Links

- [Hypermind Project](https://github.com/lklynet/hypermind)
- [Report Issues](https://github.com/synssins/hypermind-ha/issues)

## License

MIT License - see LICENSE for details.
