# NexusRecon 🔍

**A Recursive OSINT Engine**
*Created by Al-hassan shehade*

NexusRecon is an advanced, asynchronous OSINT framework designed to automate the discovery of publicly available information. It combines recursive username cross-referencing, intelligent Google dorking, and optional network scanning (`nmap`) to build a complete digital profile of a target in minutes.

## 🚀 Features
- **Recursive Username Scanning**: Searches deeply across multiple platforms and databases.
- **Google Dorking**: Automatically performs targeted searches to uncover sensitive public information.
- **Network Reconnaissance**: Optional `--nmap` integration to scan associated IPs or domains.
- **Asynchronous Architecture**: Uses Python's `asyncio` for fast, non-blocking multi-threaded execution.

## 🛠️ Installation
**On Linux / Termux (Mobile):**
1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/nexusrecon.git
   cd nexusrecon
