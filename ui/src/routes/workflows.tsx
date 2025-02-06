/**
 * @license Apache-2.0
 * 
 * Workflows layout route
 */

import { createFileRoute, Outlet } from '@tanstack/react-router'

export const Route = createFileRoute('/workflows')({
  component: WorkflowsLayout,
})

function WorkflowsLayout() {
  return (
    <div className="container mx-auto px-4 py-8">
      <Outlet />
    </div>
  )
} 