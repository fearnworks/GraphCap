=================================
UI Architecture
=================================

graphcap Studio's UI architecture follows a hybrid modular pattern that emphasizes separation of concerns, reusability, and maintainability.

Directory Structure
=================

The UI codebase is organized into the following key directories:

.. code-block:: text

   ui/src/
   ├── app/           # Application initialization and global config
   ├── features/      # Feature-specific modules
   ├── common/        # Shared components and utilities  
   ├── routes/        # Route-specific modules for tanstack router
   └── services/      # Application-wide services

Core Principles
=============

1. **Modular Organization**: Code is organized by feature and responsibility
2. **Component Separation**: Clear distinction between presentational and container components
3. **Code Reusability**: Common utilities and components are centralized
4. **Service Isolation**: Business logic is separated from UI concerns

Key Directories
=============

app/
----
The ``app/`` directory contains core application initialization code and global configuration:

- Entry point (``main.tsx``)
- Global providers (Theme, Auth, etc.)
- High-level routing logic
- Global styling and configuration

features/
--------
The ``features/`` directory contains domain-specific code organized into feature modules. Each feature has:

- ``components/``: Presentational UI components
- ``containers/``: Logic-heavy components with state management
- ``hooks/``: Feature-specific custom hooks
- ``services/``: (Optional) Feature-specific business logic

Example feature structure:

.. code-block:: text

   features/gallery/
   ├── components/     # "Dumb" UI components
   ├── containers/     # "Smart" components with logic
   ├── hooks/         # Feature-specific hooks
   └── services/      # Gallery-specific services

common/
-------
The ``common/`` directory contains reusable code shared across features:

- ``components/``: Generic UI components (buttons, forms, etc.)
- ``hooks/``: Shared custom hooks
- ``utils/``: Utility functions and constants
- ``styles/``: Global styling assets and Tailwind configuration

services/
--------
The ``services/`` directory contains application-wide business logic and integrations:

- API clients
- Data transformation services
- Shared business logic
- External integrations

Best Practices
============

Component Architecture
--------------------
- Separate presentational and container components
- Keep components focused and single-purpose
- Use TypeScript for type safety
- Follow Tailwind CSS conventions for styling

Code Organization
---------------
- Place feature-specific code in appropriate feature directory
- Move reusable code to ``common/``
- Keep services stateless when possible
- Document complex logic and APIs

State Management
--------------
- Use React hooks for local state
- Implement container components for complex state
- Keep state close to where it's used
- Document state management patterns

Testing
-------
- Write unit tests for services
- Test components in isolation
- Document testing patterns and expectations
- Use TypeScript to catch type-related issues early

Development Workflow
==================

1. **Feature Development**:
   - Create new feature directory if needed
   - Implement components and logic
   - Write tests and documentation

2. **Common Code**:
   - Identify reusable patterns
   - Move shared code to ``common/``
   - Update documentation

3. **Services**:
   - Implement business logic in services
   - Keep services focused and testable
   - Document APIs and interfaces

4. **Integration**:
   - Connect components to services
   - Test integrations
   - Update documentation

Conclusion
=========

This architecture promotes:

- Clear separation of concerns
- Code reusability
- Maintainable codebase
- Scalable feature development
- Consistent development patterns

The modular approach allows teams to work independently on features while maintaining consistency through shared components and services. 