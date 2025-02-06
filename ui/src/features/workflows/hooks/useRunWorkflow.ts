/**
 * @license Apache-2.0
 * 
 * Hook for running workflows and tracking execution
 */

import { useMutation } from '@tanstack/react-query'
import { API_BASE_URL } from '../../../services/api'

interface RunWorkflowParams {
  workflowId: string
  startNode?: string
}

interface RunWorkflowResponse {
  job_id: string
  pipeline_id: string
  status: string
}

async function runWorkflow({ workflowId, startNode }: RunWorkflowParams): Promise<RunWorkflowResponse> {
  const url = `${API_BASE_URL}/workflows/${workflowId}/run${startNode ? `?start_node=${startNode}` : ''}`
  
  const response = await fetch(url, {
    method: 'POST',
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to run workflow')
  }

  return response.json()
}

export function useRunWorkflow() {
  return useMutation({
    mutationFn: runWorkflow,
  })
} 