# Build Your Own Aircraft Radar

This guide describes the process of creating your own ADS-B data reception station for aircraft tracking, from hardware selection to software integration.

## 1. Why do this?

Deploying your own radar solves several tasks:
* **Community support:** Projects collecting flight data critically need a dense network of receivers for verification and confidence in their data. There are fewer enthusiasts in this field than it might seem.
* **Engineering experience:** This is a great way to refresh your knowledge of radio receivers and signal reception technologies—an essential foundation that young engineers often ignore.
* **FlightRadar24 bonuses:** Program participants receive *Contributor* status. This unlocks access to weather data (which is hard to find elsewhere), real-time tracking, interesting UI settings, and other premium features, which is especially useful when picking friends up at the airport (or if you are a taxi driver).

## 2. Hardware

To build the radar, you will need the following equipment:

* **Compute module:** Raspberry Pi 2, 3, 4, or 5 (FlightRadar recommends at least version 4, but the system works successfully on the Pi 2). A suitably sized SD card is also required.
* **Receiver:** Any SDR USB module (e.g., RTL2838 DVB-T).
* **1090 MHz Antenna:**
    * *Ready-made solution:* You can buy an antenna specifically designed for this frequency (available on Aliexpress or Temu).
    * *DIY solution:* Building it yourself is a much more fun and interesting process. Examples of simple DIY antennas can be found [here (e.g., "pepsy can")](https://discussions.flightaware.com/t/three-easy-diy-antennas-for-beginners/16348).

### 💡 Assembly and Placement Recommendations:
* **Visibility:** Carefully choose the location for your antenna. It is crucial to review the [official FlightRadar placement recommendations](https://www.flightradar24.com/files/positioning_mode-s_antenna.pdf) beforehand to maximize your antenna's "field of view".
* **Cable:** The shorter the wires from the antenna to the SDR, the better (ideally, the connection should be "one-to-one").
* **Filtering and amplification:** If you are using an amplifier, be sure to install it with a bandpass filter. The personally recommended chain order is: `Antenna` ➔ `Amplifier` ➔ `Filter` ➔ `Receiver`.

## 3. Software Installation and Configuration

### System Preparation
1.  **OS Identification:** Verified system is Raspbian 13 (Trixie) on Raspberry Pi; it is recommended to use Raspberry Pi OS Lite.
2.  **USB Verification:** Confirm that your RTL2838 DVB-T dongle is connected (e.g. ID `0bda:2838`).

### Clean Installation (`readsb` and `tar1090`)
Update your package lists and run the automated installation script:

```bash
sudo apt-get update
sudo bash -c "$(wget -O - https://raw.githubusercontent.com/wiedehopf/adsb-scripts/master/readsb-install.sh)"

```

### Validation

Ensure the system is receiving data correctly:

* Verify that the `readsb` service is running.
* Verify live data reception using: `sudo TERM=linux viewadsb`.
* Verify the presence of JSON output at: `/run/readsb/aircraft.json`.

### Installing the FlightRadar24 Client

Run the FR24 installation script:

```bash
sudo bash -c "$(wget -O - https://repo-feed.flightradar24.com/install_fr24_feed.sh)"

```

In the FR24 configuration file (`/etc/fr24feed.ini`), you must specify the following two lines to properly integrate with `readsb`:

```ini
receiver="beast-tcp"
host="127.0.0.1:30005"

```

## 4. Web Interface and Local API

### Browser Viewing (UI)

After a successful installation, you can watch the aircraft on an interactive real-time map directly through your server. To access the web interface, open your browser and navigate to:
`http://<IP_ADDRESS>/tar1090/` (for example, `http://192.168.42.48/tar1090/`)

### Programmatic Access (API)

If you need to retrieve the raw data programmatically, use the following local network endpoints:

* **Primary Path:** `http://<IP_ADDRESS>/tar1090/data/aircraft.json`
* **Alternative Path:** `http://<IP_ADDRESS>:8504/data/aircraft.json`

### Terminology

* **SQW (Squawk):** Transponder code (the airplane's radio "channel").
* **FLIGHT:** Callsign or flight number ([read more about callsigns here](https://www.flightradar24.com/blog/clearing-up-call-sign-confusion/)).

### Data Schema (aircraft.json)

Each entry in the `aircraft` array from `tar1090` contains the following data:

| Field | Description | Example |
| --- | --- | --- |
| **hex** | Unique ICAO 24-bit address (hexadecimal) | `4ca808` |
| **flight** | Callsign / Flight number (ICAO airline code + number) | `RYR18TX` |
| **alt_baro** | Barometric altitude (feet) | `36000` |
| **gs** | Ground speed (knots) | `422.3` |
| **track** | True track / Course (degrees) | `272.04` |
| **lat / lon** | GPS Coordinates | `44.42, 19.49` |
| **squawk** | Transponder squawk code | `4137` |
| **rssi** | Signal strength (dBFS). Closer to 0 is stronger | `-29.3` |
| **seen** | Seconds since the last message was received | `9.8` |
| **messages** | Total messages received from this aircraft | `1886` |
| **nav_altitude_mcp** | Target altitude set on Autopilot/MCP | `36000` |


## 5. Additional Data Sources (APIs)

To enrich the aircraft information, you can use external services:

1. **[OpenSky Network](https://opensky-network.org/data/datasets#d5):** Offers an excellent dataset, and their addons database is especially useful.
2. **[AirPortData](https://www.airport-data.com/api/doc.php):** Offers a free but incomplete aircraft database. It provides small preview images linking to full-sized, high-quality photos on their service.
3. **[ADS-B Exchange](https://rapidapi.com/adsbx/api/adsbexchange-com1/pricing):** A paid database. Despite your participation in data collection, getting free API access from them is difficult (unless you reverse-engineer their internal map API).
4. **[Planespotters.net](https://www.planespotters.net/search?q=06A10C):** Allows converting HEX to a human-readable format. The service has its own API for potential integrations.

---

## 6. Further Reading

* [Hardware integration (Ian Renton)](https://ianrenton.com/hardware/planesailing/)
* [AIS receivers and related technologies (Sarcnet)](https://www.sarcnet.org/ais-receiver.html)
* [ADS-B Exchange API Documentation and Pricing (RapidAPI)](https://rapidapi.com/adsbx/api/adsbexchange-com1/pricing)
