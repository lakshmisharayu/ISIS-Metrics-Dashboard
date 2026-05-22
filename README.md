# ISIS-Metrics-Dashboard
ISIS-Metrics-Dashboard
# ISIS Metrics Dashboard

A comprehensive web-based monitoring dashboard for ISIS routing protocol metrics collected from Junos routers. Built with Flask, integrated with jsnapy for secure SSH connectivity.

## Features

- 🚀 **Real-time ISIS Metrics Collection** - Automated SSH data collection from Junos devices
- 📊 **Interactive Dashboard** - Beautiful web UI with Plotly charts
- 📈 **Metrics Tracked**:
  - Total number of LSPs (Link State Packets)
  - LSP database size
  - Number of ISIS nodes
  - L1/L2 split count
  - Total adjacencies
  - ISIS-enabled interfaces
  - Database overload status
- 🔄 **Historical Data** - 24+ hour retention with trend analysis
- 🐳 **Docker Ready** - Pre-configured for containerized deployment
- 🔐 **Secure SSH** - Uses paramiko with credential management
- 📱 **Responsive Design** - Works on desktop, tablet, mobile

## Installation

### Prerequisites
- Python 3.7+
- pip package manager
- SSH access to Junos routers
- Docker (optional, for containerized deployment)

### Local Installation

1. **Clone the repository**
```bash
git clone https://github.com/LakshmiSharayu/ISIS-Metrics-Dashboard.git
cd ISIS-Metrics-Dashboard
