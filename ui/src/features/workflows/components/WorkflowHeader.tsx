/**
 * @license Apache-2.0
 * 
 * Workflow header component with metadata and actions
 */

import { useNavigate } from '@tanstack/react-router'
import { Workflow } from '../../../services/workflows'

interface WorkflowHeaderProps {
  workflow: Workflow
  onRun?: () => void
}

export function WorkflowHeader({ workflow, onRun }: WorkflowHeaderProps) {
  const navigate = useNavigate()

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {workflow.name}
          </h1>
          {workflow.description && (
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {workflow.description}
            </p>
          )}
          <div className="flex gap-4 text-sm text-gray-500 dark:text-gray-400">
            <div>Created: {new Date(workflow.created_at).toLocaleString()}</div>
            <div>Updated: {new Date(workflow.updated_at).toLocaleString()}</div>
            {workflow.workflow_metadata?.version && (
              <div>Version: {workflow.workflow_metadata.version}</div>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => navigate({ to: '/workflows' })}
            className="px-4 py-2 text-gray-700 dark:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            Back
          </button>
          {onRun && (
            <button
              onClick={onRun}
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
            >
              Run Workflow
            </button>
          )}
        </div>
      </div>
    </div>
  )
} 