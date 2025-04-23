# Status Page Collector

A simple web application that collects and displays status information from various services including GitHub, AWS, Grafana Cloud, and Opsgenie.

## Features

- Real-time status monitoring for multiple services
- Clean, responsive web interface
- Auto-refresh every 5 minutes
- Asynchronous status fetching for better performance

## Requirements

- Python 3.8+
- pip (Python package installer)

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd status-page-collector
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python status_collector.py
```

2. Open your web browser and navigate to:
```
http://localhost:8000
```

The dashboard will automatically refresh every 5 minutes to show the latest status information.

## Services Monitored

- GitHub
- AWS
- Grafana Cloud
- Opsgenie

## Contributing

Feel free to submit issues and enhancement requests! 