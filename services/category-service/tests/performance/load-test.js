const autocannon = require('autocannon');
const path = require('path');

// Performance test configuration
const config = {
  // Test target
  url: process.env.TEST_URL || 'http://localhost:8005',

  // Test parameters
  connections: parseInt(process.env.TEST_CONNECTIONS) || 10,
  duration: parseInt(process.env.TEST_DURATION) || 30,
  pipelining: parseInt(process.env.TEST_PIPELINING) || 1,

  // Performance thresholds
  thresholds: {
    latency: {
      p95: 200, // 95th percentile should be under 200ms
      p99: 500  // 99th percentile should be under 500ms
    },
    throughput: {
      min: 100 // Minimum requests per second
    },
    errors: {
      max: 0.01 // Maximum 1% error rate
    }
  }
};

/**
 * Run performance test for a specific endpoint
 */
async function runTest(testConfig) {
  console.log(`\n🚀 Running performance test: ${testConfig.name}`);
  console.log(`   URL: ${testConfig.url}`);
  console.log(`   Connections: ${config.connections}`);
  console.log(`   Duration: ${config.duration}s`);
  console.log(`   Expected throughput: >${config.thresholds.throughput.min} req/s`);
  console.log(`   Expected latency p95: <${config.thresholds.latency.p95}ms`);

  try {
    const result = await autocannon({
      url: testConfig.url,
      connections: config.connections,
      duration: config.duration,
      pipelining: config.pipelining,
      method: testConfig.method || 'GET',
      headers: testConfig.headers || {},
      body: testConfig.body ? JSON.stringify(testConfig.body) : undefined
    });

    // Analyze results
    const analysis = analyzeResults(result, testConfig.name);

    // Print results
    printResults(result, analysis);

    return analysis;
  } catch (error) {
    console.error(`❌ Test failed: ${error.message}`);
    return { passed: false, error: error.message };
  }
}

/**
 * Analyze test results against thresholds
 */
function analyzeResults(result, testName) {
  const analysis = {
    name: testName,
    passed: true,
    issues: [],
    metrics: {
      throughput: result.requests.average,
      latency: {
        p95: result.latency.p95,
        p99: result.latency.p99,
        mean: result.latency.mean
      },
      errorRate: (result.errors / result.requests.total) * 100,
      totalRequests: result.requests.total
    }
  };

  // Check throughput
  if (result.requests.average < config.thresholds.throughput.min) {
    analysis.passed = false;
    analysis.issues.push(
      `Low throughput: ${result.requests.average} req/s (expected >${config.thresholds.throughput.min})`
    );
  }

  // Check latency
  if (result.latency.p95 > config.thresholds.latency.p95) {
    analysis.passed = false;
    analysis.issues.push(
      `High p95 latency: ${result.latency.p95}ms (expected <${config.thresholds.latency.p95}ms)`
    );
  }

  if (result.latency.p99 > config.thresholds.latency.p99) {
    analysis.passed = false;
    analysis.issues.push(
      `High p99 latency: ${result.latency.p99}ms (expected <${config.thresholds.latency.p99}ms)`
    );
  }

  // Check error rate
  const errorRate = (result.errors / result.requests.total) * 100;
  if (errorRate > config.thresholds.errors.max * 100) {
    analysis.passed = false;
    analysis.issues.push(
      `High error rate: ${errorRate.toFixed(2)}% (expected <${config.thresholds.errors.max * 100}%)`
    );
  }

  return analysis;
}

/**
 * Print formatted test results
 */
function printResults(result, analysis) {
  console.log(`\n📊 Results for ${analysis.name}:`);
  console.log(`   Status: ${analysis.passed ? '✅ PASSED' : '❌ FAILED'}`);
  console.log(`   Throughput: ${result.requests.average.toFixed(1)} req/s`);
  console.log(`   Latency (mean): ${result.latency.mean.toFixed(1)}ms`);
  console.log(`   Latency (p95): ${result.latency.p95.toFixed(1)}ms`);
  console.log(`   Latency (p99): ${result.latency.p99.toFixed(1)}ms`);
  console.log(`   Total requests: ${result.requests.total}`);
  console.log(`   Errors: ${result.errors}`);
  console.log(`   Error rate: ${((result.errors / result.requests.total) * 100).toFixed(2)}%`);

  if (!analysis.passed) {
    console.log(`\n⚠️  Issues found:`);
    analysis.issues.forEach(issue => console.log(`   - ${issue}`));
  }
}

/**
 * Main test suite
 */
async function main() {
  console.log('🔥 Category Service Performance Test Suite');
  console.log('=' .repeat(50));

  const tests = [
    {
      name: 'Health Check',
      url: `${config.url}/health`
    },
    {
      name: 'Readiness Check',
      url: `${config.url}/health/ready`
    },
    {
      name: 'List Root Categories',
      url: `${config.url}/categories?parent_id=null`
    },
    {
      name: 'List Categories with Children',
      url: `${config.url}/categories?include_children=true`
    },
    {
      name: 'List Categories with Product Count',
      url: `${config.url}/categories?include_product_count=true`
    },
    {
      name: 'Get Category by ID',
      url: `${config.url}/categories/1`
    },
    {
      name: 'Get Category Hierarchy',
      url: `${config.url}/categories/1/hierarchy`
    },
    {
      name: 'Search Categories',
      url: `${config.url}/categories/search?q=electronics`
    },
    {
      name: 'Get Category Products',
      url: `${config.url}/categories/1/products?limit=20`
    }
  ];

  const results = [];

  // Run all tests
  for (const test of tests) {
    const result = await runTest(test);
    results.push(result);

    // Brief pause between tests
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  // Summary
  console.log('\n📈 PERFORMANCE TEST SUMMARY');
  console.log('=' .repeat(50));

  const passedTests = results.filter(r => r.passed).length;
  const totalTests = results.length;

  console.log(`Tests passed: ${passedTests}/${totalTests}`);

  if (passedTests === totalTests) {
    console.log('🎉 All performance tests passed!');
    process.exit(0);
  } else {
    console.log('💥 Some performance tests failed!');
    console.log('\nFailed tests:');
    results.filter(r => !r.passed).forEach(result => {
      console.log(`   - ${result.name}`);
      result.issues?.forEach(issue => console.log(`     ${issue}`));
    });
    process.exit(1);
  }
}

// Export for use in other test files
module.exports = {
  runTest,
  analyzeResults,
  config
};

// Run if called directly
if (require.main === module) {
  main().catch(error => {
    console.error('Test suite failed:', error);
    process.exit(1);
  });
}