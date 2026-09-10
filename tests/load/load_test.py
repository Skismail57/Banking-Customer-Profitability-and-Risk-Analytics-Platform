"""Load tests for API endpoints using k6."""

import os
import subprocess
import json
from pathlib import Path


def generate_k6_script():
    """Generate k6 load test script."""
    script = """
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 10 },   // Ramp up to 10 users
    { duration: '1m', target: 10 },    // Stay at 10 users
    { duration: '20s', target: 50 },   // Ramp up to 50 users
    { duration: '1m', target: 50 },    // Stay at 50 users
    { duration: '20s', target: 0 },    // Ramp down to 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests must complete below 500ms
    http_req_failed: ['rate<0.01'],     // Error rate must be less than 1%
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000';

export default function () {
  // Test health endpoint
  let healthRes = http.get(`${BASE_URL}/api/v1/health`);
  check(healthRes, {
    'health status is 200': (r) => r.status === 200,
    'health response time < 200ms': (r) => r.timings.duration < 200,
  });

  // Test customers endpoint
  let customersRes = http.get(`${BASE_URL}/api/v1/customers?page=1&page_size=10`);
  check(customersRes, {
    'customers status is 200': (r) => r.status === 200,
    'customers response time < 500ms': (r) => r.timings.duration < 500,
  });

  // Test profitability endpoint
  let profitRes = http.get(`${BASE_URL}/api/v1/profitability/aggregate`);
  check(profitRes, {
    'profitability status is 200': (r) => r.status === 200,
    'profitability response time < 500ms': (r) => r.timings.duration < 500,
  });

  // Test risk endpoint
  let riskRes = http.get(`${BASE_URL}/api/v1/risk/aggregate`);
  check(riskRes, {
    'risk status is 200': (r) => r.status === 200,
    'risk response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
"""
    
    script_path = Path(__file__).parent / 'api_load_test.js'
    script_path.write_text(script)
    return script_path


def run_load_test(api_url='http://localhost:8000'):
    """Run k6 load test."""
    script_path = generate_k6_script()
    
    # Set environment variable for API URL
    env = os.environ.copy()
    env['API_URL'] = api_url
    
    # Run k6
    try:
        result = subprocess.run(
            ['k6', 'run', str(script_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print("Load test completed")
        print(result.stdout)
        
        if result.returncode != 0:
            print("Load test errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("Load test timed out after 5 minutes")
        return False
    except FileNotFoundError:
        print("k6 not found. Install from: https://k6.io/")
        return False


if __name__ == '__main__':
    import sys
    api_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8000'
    success = run_load_test(api_url)
    sys.exit(0 if success else 1)
