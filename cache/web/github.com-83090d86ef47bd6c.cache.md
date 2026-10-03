# mww012/instantpy
URL: https://github.com/mww012/instantpy

# mww012/instantpy

Python API Wrapper for Aruba Instant

- Stars: 9
- Forks: 7
- Watchers: 9
- Open issues: 1
- License: GNU General Public License v3.0
- Default branch: master
- Created: 2020-05-07T20:51:02Z

## Languages

- Python

## Topics

- aruba
- aruba-iap
- python
- python3

## Top Contributors

- mww012 (17 contributions)
- apaperclip (2 contributions)
- federstedt (1 contributions)
- mzac (1 contributions)

---

## README

# Aruba Instant Python API Wrapper

This module provides a Python 3 interface for the Aruba Instant 8.6 REST API.

**Please understand this project is a WIP. I'd also really appreciate some help testing. My Instant cluster is my production wifi at home. I can't thoroughly test certain calls to the API (specifically in the Configuration portion) because breaking the wifi at home would result in an unhappy household.**

For full documentation, see here.

The REST API is divided into three secions. **Monitoring**, **Action**, and **Configuration**. Details on each section are below. Logging in and out is handled by the ```login()``` and ```logout()``` methods. Logging in has a decorator method that will handle logging in if needed. You will still need to handle logging out. *See examples below.*

## Monitoring
The monitoring endpoints of the API is used for, obviously, monitoring. It is used to gather state, statistics, and logs from master, slave, or standalone Instant APs. The architecture of this portion of the API is very similar to the cli output of "show" commands. The currently supported commands are ```show clients``` and ```show aps```. More will be added shortly. There is also a generic ```show command``` method that will accept any CLI show commands and return unstructured text.

Feel free to open an issue and request support for more commands if the structured output would be helpful. I can also add support for different OS versions (at least back to 8.5) if it would be helpful.

 NOTE: The response from the API is currently unstructred text and requires parsing with RegEx. 
 This lends itself to breaking easily between versions. My current testing has been against 8.6.

## Action
The action endpoints are used for configuring AP specific settings. See below for supported endpoints.

Endpoint | Method | Description
--- | --- | ---
Hostname | hostname() | Set the hostname of a specific IAP.
Swarm Mode | swarm() | Set an AP to be standalone or part of a swarm cluster.
Static Channel and Power | channel() | Set the tx channel and power of the radios of a specific IAP.
Zone | zone() | Set the zone of a specific IAP.
Antenna Gain | antenna_gain() | Set the specific antenna gain when external antennas are used.
Enable and Disable Radios | radio_state() | Enable or disable a radio in an AP.
Generic Show Command | show_cmd() | Returns unstructured output text from any "show" command provided.

## Configuration
Configuration endpoints are used to configure an Instant Virtual Controller. See table below for supported