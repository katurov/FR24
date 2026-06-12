# ADSB Multi-Radar Setup Final Report
**Date:** Thursday, June 4, 2026

## 1. Network Infrastructure
The system consists of two Raspberry Pi receivers covering different sides of the house.

### Radar #1 (Master Hub)
- **IP Address:** `192.168.42.48`
- **Hardware:** Raspberry Pi (aarch64, Debian 13)
- **Role:** Master Collector (aggregates data from Radar #2 and its own antenna)
- **FlightRadar24 ID:** `T-LYBT27`
- **Web Interface:** http://192.168.42.48/tar1090

### Radar #2 (Secondary Node)
- **IP Address:** `192.168.42.50` (via WiFi TP-LINK TL-WN725N)
- **Hardware:** Raspberry Pi (armv7l, Raspbian 13)
- **Role:** Feeds local data to Radar #1 and FR24
- **FlightRadar24 ID:** `T-LYBT26`
- **Web Interface:** http://192.168.42.50/tar1090

---

## 2. API Access (JSON)
To programmatically retrieve aircraft data, use the following endpoints:

- **Primary Path:** `http://<IP_ADDRESS>/tar1090/data/aircraft.json`
- **Alternative Path:** `http://<IP_ADDRESS>:8504/data/aircraft.json`

---

## 3. Data Schema (aircraft.json)
Each entry in the `aircraft` array contains:

| Field | Description | Example |
| :--- | :--- | :--- |
| **hex** | Unique ICAO 24-bit address (hexadecimal) | `4ca808` |
| **flight** | Callsign / Flight number (ICAO airline code + number) | `RYR18TX` |
| **alt_baro** | Barometric altitude (feet) | `36000` |
| **gs** | Ground speed (knots) | `422.3` |
| **track** | True track / Course (degrees) | `272.04` |
| **lat / lon** | GPS Coordinates | `44.42, 19.49` |
| **squawk** | Transponder squawk code | `4137` |
| **rssi** | Signal strength (dBFS). Closer to 0 is stronger. | `-29.3` |
| **seen** | Seconds since last message was received | `9.8` |
| **messages** | Total messages received from this aircraft | `1886` |
| **nav_altitude_mcp** | Target altitude set on Autopilot/MCP | `36000` |

---

## 4. Special Settings
- **WiFi Stability:** Radar #2 (.50) has a crontab heartbeat (ping every 1 min) and `powersave off` to prevent the Realtek adapter from sleeping.
- **Data Aggregation:** Radar #1 (.48) uses `--net-connector 192.168.42.50,30005,beast_in` to pull data from Radar #2 for a unified map view.
- **Auto-start:** All services (`readsb`, `fr24feed`) are enabled via `systemctl` to start on boot.
