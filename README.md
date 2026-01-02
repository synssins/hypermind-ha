# Hypermind Home Assistant Integration

A Home Assistant custom integration for monitoring Hypermind - the decentralized P2P deployment counter.

## Features

- Active Nodes Sensor with scale_ratio attribute (0.0-1.0)
- Direct Connections Sensor
- Configurable Scale Range for RGB automations
- Options Flow to adjust scale without reconfiguring

## Installation (HACS)

1. Open HACS > Custom repositories
2. Add https://github.com/synssins/hypermind-ha with category Integration
3. Install and restart Home Assistant

## Configuration

1. Go to Settings > Devices and Services > Add Integration
2. Search for Hypermind
3. Enter host, port, and scale range (min/max)

## Scale Configuration

The scale determines how the scale_ratio attribute is calculated:

- Scale Minimum (default 0): Node count that maps to 0.0 (green)
- Scale Maximum (default 10000): Node count that maps to 1.0 (red)

Examples:
- Small deployment: Set 0-500 for a more responsive color range
- Large deployment: Set 1000-50000 for high node counts

To change scale after setup: Click Configure on the integration.

## Sensor Attributes

sensor.hypermind_active_nodes exposes:
- state: Current node count
- scale_min: Configured minimum
- scale_max: Configured maximum
- scale_ratio: Normalized 0.0-1.0 value for automations

## Automation Example

Use state_attr to get the pre-calculated scale_ratio:

    state_attr("sensor.hypermind_active_nodes", "scale_ratio")

This returns a value between 0.0 and 1.0 based on your configured scale.
Use it to set RGB colors: green (0.0) to red (1.0).

## Running Hypermind

docker run -d --name hypermind --network host --restart unless-stopped -e PORT=3000 ghcr.io/lklynet/hypermind:latest

Use --network host for P2P connectivity.

## Links

- Hypermind Project: https://github.com/lklynet/hypermind
- Report Issues: https://github.com/synssins/hypermind-ha/issues

MIT License
