import aiohttp
import asyncio
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json
from pathlib import Path

# Get the current directory
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="Status Page Collector")

# Status page URLs
STATUS_PAGES = {
    'GitHub': {
        'url': 'https://www.githubstatus.com/api/v2/summary.json',
        'type': 'statusio',
        'status_page': 'https://www.githubstatus.com/'
    },
    'AWS': {
        'url': 'https://status.aws.amazon.com/healthfeed/status.json',
        'type': 'aws',
        'status_page': 'https://health.aws.amazon.com/health/status'
    },
    'Grafana Cloud': {
        'url': 'https://status.grafana.com/api/v2/summary.json',
        'type': 'statusio',
        'status_page': 'https://status.grafana.com/'
    },
    'Opsgenie': {
        'url': 'https://status.opsgenie.com/api/v2/summary.json',
        'type': 'statusio',
        'status_page': 'https://status.opsgenie.com/'
    }
}

async def fetch_status(session, service_name, service_info):
    try:
        async with session.get(service_info['url']) as response:
            if response.status == 200:
                data = await response.text()
                return service_name, {
                    'status': 'ok',
                    'data': json.loads(data),
                    'type': service_info['type']
                }
            else:
                return service_name, {
                    'status': 'error',
                    'message': f'HTTP {response.status}'
                }
    except Exception as e:
        return service_name, {
            'status': 'error',
            'message': str(e)
        }

async def get_all_statuses():
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_status(session, service_name, service_info)
            for service_name, service_info in STATUS_PAGES.items()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {name: status for name, status in results if isinstance(status, dict)}

def parse_status(service_name, status_data):
    try:
        if status_data['status'] == 'error':
            return {
                'name': service_name,
                'status': 'Unknown',
                'description': status_data.get('message', 'Unknown error'),
                'last_updated': datetime.now().isoformat(),
                'status_page': STATUS_PAGES[service_name]['status_page']
            }

        if status_data['type'] == 'statusio':
            try:
                status = status_data['data'].get('status', {})
                return {
                    'name': service_name,
                    'status': status.get('indicator', 'Unknown'),
                    'description': status.get('description', 'No description available'),
                    'last_updated': status.get('updated_at', datetime.now().isoformat()),
                    'status_page': STATUS_PAGES[service_name]['status_page']
                }
            except (KeyError, AttributeError):
                return {
                    'name': service_name,
                    'status': 'Error',
                    'description': 'Unable to parse status data',
                    'last_updated': datetime.now().isoformat(),
                    'status_page': STATUS_PAGES[service_name]['status_page']
                }
        elif status_data['type'] == 'aws':
            try:
                events = status_data['data'].get('current_events', [])
                if not events:
                    return {
                        'name': service_name,
                        'status': 'Operational',
                        'description': 'All services operating normally',
                        'last_updated': datetime.now().isoformat(),
                        'status_page': STATUS_PAGES[service_name]['status_page']
                    }
                else:
                    return {
                        'name': service_name,
                        'status': 'Disrupted',
                        'description': events[0].get('details', 'Service issues reported'),
                        'last_updated': events[0].get('date', datetime.now().isoformat()),
                        'status_page': STATUS_PAGES[service_name]['status_page']
                    }
            except (KeyError, AttributeError, IndexError):
                return {
                    'name': service_name,
                    'status': 'Error',
                    'description': 'Unable to parse status data',
                    'last_updated': datetime.now().isoformat(),
                    'status_page': STATUS_PAGES[service_name]['status_page']
                }
    except Exception as e:
        return {
            'name': service_name,
            'status': 'Error',
            'description': f'Error processing status: {str(e)}',
            'last_updated': datetime.now().isoformat(),
            'status_page': STATUS_PAGES[service_name]['status_page']
        }

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    try:
        statuses = await get_all_statuses()
        parsed_statuses = [
            parse_status(service_name, status_data)
            for service_name, status_data in statuses.items()
        ]
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "statuses": parsed_statuses}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "statuses": [{
                    'name': 'System Error',
                    'status': 'Error',
                    'description': f'Error fetching statuses: {str(e)}',
                    'last_updated': datetime.now().isoformat()
                }]
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 