/**
 * K6 Load Testing Script for PackOptima
 * 
 * Scenarios:
 * 1. 100 concurrent users, 10 optimization requests each
 * 2. 10 concurrent bulk uploads, 500 orders each
 * 3. 50 concurrent dashboard loads
 * 
 * Usage:
 *   k6 run k6_load_test.js
 *   k6 run --vus 100 --duration 30s k6_load_test.js
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const optimizationErrors = new Rate('optimization_errors');
const optimizationDuration = new Trend('optimization_duration');
const analyticsErrors = new Rate('analytics_errors');
const analyticsDuration = new Trend('analytics_duration');

// Configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Test configuration
export const options = {
    scenarios: {
        // Scenario 1: Optimization load
        optimization_load: {
            executor: 'constant-vus',
            vus: 100,
            duration: '5m',
            tags: { scenario: 'optimization' },
        },
        
        // Scenario 2: Bulk upload load
        bulk_upload_load: {
            executor: 'constant-vus',
            vus: 10,
            duration: '5m',
            startTime: '5m',
            tags: { scenario: 'bulk_upload' },
        },
        
        // Scenario 3: Dashboard load
        dashboard_load: {
            executor: 'constant-vus',
            vus: 50,
            duration: '5m',
            startTime: '10m',
            tags: { scenario: 'dashboard' },
        },
    },
    
    thresholds: {
        // Overall thresholds
        http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
        http_req_failed: ['rate<0.01'],    // Error rate under 1%
        
        // Optimization thresholds
        'optimization_duration': ['p(95)<100'],  // Single product < 100ms
        'optimization_errors': ['rate<0.01'],
        
        // Analytics thresholds
        'analytics_duration': ['p(95)<200'],  // Analytics < 200ms
        'analytics_errors': ['rate<0.01'],
    },
};

// Setup function - runs once before test
export function setup() {
    // Login and get token
    const loginRes = http.post(`${BASE_URL}/api/v1/auth/login`, JSON.stringify({
        email: 'test@example.com',
        password: 'testpassword123',
    }), {
        headers: { 'Content-Type': 'application/json' },
    });
    
    const token = loginRes.json('access_token');
    
    // Get sample product and box IDs
    const productsRes = http.get(`${BASE_URL}/api/v1/products`, {
        headers: { 'Authorization': `Bearer ${token}` },
    });
    
    const products = productsRes.json();
    const productIds = products.slice(0, 10).map(p => p.id);
    
    return {
        token: token,
        productIds: productIds,
    };
}

// Main test function
export default function(data) {
    const headers = {
        'Authorization': `Bearer ${data.token}`,
        'Content-Type': 'application/json',
    };
    
    // Determine which scenario to run based on tags
    const scenario = __ENV.SCENARIO || 'all';
    
    if (scenario === 'optimization' || scenario === 'all') {
        optimizationScenario(data, headers);
    }
    
    if (scenario === 'bulk_upload' || scenario === 'all') {
        bulkUploadScenario(data, headers);
    }
    
    if (scenario === 'dashboard' || scenario === 'all') {
        dashboardScenario(data, headers);
    }
    
    sleep(1);
}

function optimizationScenario(data, headers) {
    group('Optimization Requests', function() {
        // Single product optimization
        const productId = data.productIds[Math.floor(Math.random() * data.productIds.length)];
        
        const startTime = Date.now();
        const res = http.post(
            `${BASE_URL}/api/v1/optimize`,
            JSON.stringify({ product_id: productId }),
            { headers: headers }
        );
        const duration = Date.now() - startTime;
        
        optimizationDuration.add(duration);
        
        const success = check(res, {
            'optimization status is 200': (r) => r.status === 200,
            'optimization has result': (r) => r.json('recommended_box') !== undefined,
            'optimization under 100ms': () => duration < 100,
        });
        
        optimizationErrors.add(!success);
    });
    
    group('Async Optimization', function() {
        const productId = data.productIds[Math.floor(Math.random() * data.productIds.length)];
        
        // Submit async task
        const submitRes = http.post(
            `${BASE_URL}/api/v1/optimize/async`,
            JSON.stringify({ product_id: productId }),
            { headers: headers }
        );
        
        check(submitRes, {
            'async submit status is 202': (r) => r.status === 202,
            'async submit has task_id': (r) => r.json('task_id') !== undefined,
        });
        
        const taskId = submitRes.json('task_id');
        
        if (taskId) {
            // Check task status
            const statusRes = http.get(
                `${BASE_URL}/api/v1/tasks/${taskId}`,
                { headers: headers }
            );
            
            check(statusRes, {
                'task status is 200': (r) => r.status === 200,
                'task has status field': (r) => r.json('status') !== undefined,
            });
        }
    });
}

function bulkUploadScenario(data, headers) {
    group('Bulk Upload', function() {
        // Generate CSV content
        let csvContent = 'order_number,customer_name,product_sku,quantity\n';
        
        const numOrders = 50 + Math.floor(Math.random() * 50);  // 50-100 orders
        
        for (let i = 0; i < numOrders; i++) {
            const orderNum = `BULK-${Math.floor(Math.random() * 90000) + 10000}`;
            const customer = `Customer ${i}`;
            
            // Add 2-5 items per order
            const numItems = 2 + Math.floor(Math.random() * 4);
            for (let j = 0; j < numItems; j++) {
                const sku = `PROD-${Math.floor(Math.random() * 900) + 100}`;
                const qty = Math.floor(Math.random() * 10) + 1;
                csvContent += `${orderNum},${customer},${sku},${qty}\n`;
            }
        }
        
        // Upload CSV
        const formData = {
            file: http.file(csvContent, 'orders.csv', 'text/csv'),
        };
        
        const uploadRes = http.post(
            `${BASE_URL}/api/v1/bulk-upload`,
            formData,
            { headers: headers }
        );
        
        check(uploadRes, {
            'bulk upload status is 202': (r) => r.status === 202,
            'bulk upload has upload_id': (r) => r.json('upload_id') !== undefined,
        });
        
        const uploadId = uploadRes.json('upload_id');
        
        if (uploadId) {
            // Check upload status
            const statusRes = http.get(
                `${BASE_URL}/api/v1/bulk-upload/${uploadId}`,
                { headers: headers }
            );
            
            check(statusRes, {
                'upload status is 200': (r) => r.status === 200,
                'upload has total_orders': (r) => r.json('total_orders') !== undefined,
            });
        }
    });
}

function dashboardScenario(data, headers) {
    group('Dashboard Analytics', function() {
        // Analytics summary
        const startTime = Date.now();
        const summaryRes = http.get(
            `${BASE_URL}/api/v1/analytics/summary?period=30`,
            { headers: headers }
        );
        const duration = Date.now() - startTime;
        
        analyticsDuration.add(duration);
        
        const success = check(summaryRes, {
            'analytics summary status is 200': (r) => r.status === 200,
            'analytics summary has data': (r) => r.json('total_products') !== undefined,
            'analytics summary under 200ms': () => duration < 200,
        });
        
        analyticsErrors.add(!success);
        
        // Box usage
        http.get(
            `${BASE_URL}/api/v1/analytics/box-usage`,
            { headers: headers }
        );
        
        // Shipping costs
        http.get(
            `${BASE_URL}/api/v1/analytics/shipping-cost?period=30`,
            { headers: headers }
        );
        
        // Trends
        http.get(
            `${BASE_URL}/api/v1/analytics/trends?months=6`,
            { headers: headers }
        );
    });
    
    group('Dashboard Lists', function() {
        // List products
        http.get(`${BASE_URL}/api/v1/products`, { headers: headers });
        
        // List boxes
        http.get(`${BASE_URL}/api/v1/boxes`, { headers: headers });
        
        // List orders
        http.get(`${BASE_URL}/api/v1/orders`, { headers: headers });
    });
}

// Teardown function - runs once after test
export function teardown(data) {
    console.log('Load test completed');
}
