# Bambu Lab A1 Timelapse System

Welcome! This repository contains **two independent components** that work together to replace the stock timelapse on your Bambu Lab A1 printer.

| Folder | Role |
|--------|------|
| [`client/`](client/readme.md) | Runs on a Raspberry Pi; captures layer‑by‑layer photos, builds videos and controls LEDs |
| [`server/`](server/readme.md) | Hosts the web dashboard, REST/WS API and handles video distribution, security & tunnelling |

Head to the **component README** that matches what you want to set up:

- 👷 **Client setup & usage:** [`client/README.md`](client/readme.md)
- 🌐 **Server setup & hosting:** [`server/README.md`](server/readme.md)

---

### Quick start (TL;DR)
```bash
# 1. Flash Raspberry Pi OS Lite and ssh in

# 2. Clone the repo and pick the part you need
$ git clone https://github.com/Jannnesi/Code.git
$ cd Code

# 3. Follow the instructions in the chosen README
$ less client/README.md   # or
$ less server/README.md
```

> **Tip:** If you only need the Pi‑side camera controller you can ignore the server folder entirely, and vice‑versa.

© 2025 Janne Siirtola.  Licensed under the MIT License.
