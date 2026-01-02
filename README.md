# Hypermind Home Assistant Integration

A Home Assistant custom integration for monitoring Hypermind - the decentralized P2P deployment counter.

## Features

- Active Nodes Sensor: Shows total Hypermind instances running worldwide
- Direct Connections Sensor: Shows how many peers your node is connected to
- UI Configuration: Easy setup via Home Assistant Integrations page
- Real-time Updates: Polls the Hypermind API every 5 seconds

## Installation (HACS)

1. Open HACS in Home Assistant
2. Click three dots menu, Custom repositories
3. Add https://github.com/synssins/hypermind-ha with category Integration
4. Click Install
5. Restart Home Assistant

## Configuration

1. Go to Settings, Devices and Services, Add Integration
2. Search for Hypermind
3. Enter your Hypermind host and port

## Sensors

- sensor.hypermind_active_nodes - Total active nodes
- sensor.hypermind_direct_connections - Direct P2P connections

## Automation Examples

See the README on GitHub for complete automation examples including:

1. RGBW Light Color by Node Count
2. Milestone Announcements via TTS
3. Push Notification on Swarm Growth
4. Binary Sensor for Swarm Online status
5. Dashboard Gauge Card
6. Low Connection Alert
7. Daily Statistics Log
8. WLED Strip Visualization

## Running Hypermind

docker run -d --name hypermind --network host --restart unless-stopped -e PORT=3000 ghcr.io/lklynet/hypermind:latest

Use --network host for P2P connectivity to work properly.

## Links

- Hypermind Project: https://github.com/lklynet/hypermind
- Report Issues: https://github.com/synssins/hypermind-ha/issues

MIT License