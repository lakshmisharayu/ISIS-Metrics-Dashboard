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
1. Clone the repository
```bash
git clone https://github.com/LakshmiSharayu/ISIS-Metrics-Dashboard.git
cd ISIS-Metrics-Dashboard
2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Configure devices Edit config/devices.yml with your router details:
hosts:
  router1:
    host: 192.168.1.100
    username: admin
    password: "your_password"
    port: 22

5. Run application
python app.py
Access dashboard at: http://localhost:5000
### Prerequisites
- Python 3.7+
- pip package manager
- SSH access to Junos routers
- Docker (optional, for containerized deployment)
