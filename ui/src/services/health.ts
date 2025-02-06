/**
 * @license Apache-2.0
 * 
 * Health check service for server connectivity monitoring
 * 
 * @module HealthService
 */

import { API_BASE_URL } from './api'

export interface HealthStatus {
  status: string
  latency?: number
  serverInfo?: {
    version?: string
    environment?: string
    timestamp?: string
  }
  connectionDetails?: {
    endpoint: string
    responseTime: number
    statusCode: number
  }
}

/**
 * Check server health and connectivity
 * 
 * @returns Health status including latency and connection details
 * @throws Error if server is unreachable
 */
export async function checkServerHealth(): Promise<HealthStatus> {
  const startTime = performance.now()
  const endpoint = `${API_BASE_URL}/health`
  
  console.info(`Checking server health at ${endpoint}`)
  
  try {
    const response = await fetch(endpoint)
    const latency = performance.now() - startTime

    console.debug('Server response received', {
      status: response.status,
      statusText: response.statusText,
      latency: `${Math.round(latency)}ms`,
      headers: Object.fromEntries(response.headers.entries())
    })

    if (!response.ok) {
      const errorMessage = `Health check failed with status: ${response.status} (${response.statusText})`
      console.error(errorMessage)
      throw new Error(errorMessage)
    }

    const data = await response.json()
    
    const healthStatus: HealthStatus = {
      status: data.status,
      latency: Math.round(latency),
      serverInfo: {
        version: data.version,
        environment: data.environment,
        timestamp: new Date().toISOString()
      },
      connectionDetails: {
        endpoint,
        responseTime: Math.round(latency),
        statusCode: response.status
      }
    }

    console.info('Server health check successful', healthStatus)
    return healthStatus

  } catch (error) {
    const failureTime = Math.round(performance.now() - startTime)
    
    console.error('Health check failed', {
      error: error instanceof Error ? error.message : 'Unknown error',
      endpoint,
      failureTime: `${failureTime}ms`
    })

    return {
      status: 'error',
      latency: failureTime,
      connectionDetails: {
        endpoint,
        responseTime: failureTime,
        statusCode: 0 // Indicates connection failure
      }
    }
  }
} 