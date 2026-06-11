# ADSB Receiver Setup Success Report
**Date:** Thursday, June 4, 2026
**Target:** 192.168.42.49 (Raspberry Pi, Raspbian 13 trixie)

## Success Summary
The ADSB receiver is fully functional. It is currently decoding live signals from the RTL-SDR USB dongle and providing a local web interface for tracking.

### Access Details
- **Local Web Interface:** http://192.168.42.49/tar1090
- **Status:** Active & Receiving data (verified via `viewadsb` and `aircraft.json`)

## Steps Taken to Success
1. **OS Identification:** Verified system is Raspbian 13 (trixie) on Raspberry Pi.
2. **USB Verification:** Confirmed RTL2838 DVB-T dongle is connected (ID 0bda:2838).
3. **Clean Installation:** 
   - Updated package lists: `sudo apt-get update`
   - Installed `readsb` and `tar1090` via the wiedehopf installer script:
     `sudo bash -c "$(wget -O - https://raw.githubusercontent.com/wiedehopf/adsb-scripts/master/readsb-install.sh)"`
4. **Validation:** 
   - Verified `readsb` service is running.
   - Verified live data reception using `sudo TERM=linux viewadsb`.
   - Verified JSON output in `/run/readsb/aircraft.json`.
