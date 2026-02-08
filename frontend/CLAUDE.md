# Phase-2 Frontend CLAUDE.md - Next.js Implementation

## Project Overview

This file provides implementation guidelines for the Phase-2 frontend using Next.js 16+, TypeScript, and Tailwind CSS. The frontend serves as the user interface layer for the Evolution of Todo project, providing a responsive and accessible web application.

## Technology Stack

### Core Technologies
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React state, Context API, or Next.js built-in features
- **API Client**: Custom fetch utilities or libraries like axios

### Project Structure
```
frontend/
├── app/                   # Next.js App Router pages
│   ├── layout.tsx         # Root layout component
│   ├── page.tsx           # Home/dashboard page
│   ├── login/page.tsx     # Login page
│   ├── register/page.tsx  # Registration page
│   └── tasks/page.tsx     # Task management page
├── components/            # Reusable UI components
│   ├── auth/             # Authentication components
│   ├── task/             # Task management components
│   ├── ui/               # Generic UI components
│   └── layout/           # Layout components
├── services/              # API client and utilities
│   ├── api/              # API client functions
│   │   ├── authService.ts
│   │   └── taskService.ts
│   └── auth/             # Authentication utilities
│       └── authUtils.ts
├── types/                 # TypeScript type definitions
│   ├── auth.ts
│   ├── task.ts
│   └── user.ts
├── contexts/              # React Context providers
│   └── AuthContext.tsx
├── hooks/                 # Custom React hooks
│   └── useAuth.ts
├── styles/                # Global styles
│   └── globals.css
├── utils/                 # Utility functions
│   └── helpers.ts
└── public/                # Static assets
    └── favicon.ico
```

## App Router Structure

### Route Organization
- Use Next.js App Router (app directory)
- Create nested routes for complex features
- Implement dynamic routes with `[id]` for individual resources
- Use route groups for feature organization
- Implement error boundaries for error handling

### Page Structure
- Each route segment has a `page.tsx` file
- Use `layout.tsx` for shared UI elements
- Implement `loading.tsx` for loading states
- Use `error.tsx` for error boundaries
- Implement `not-found.tsx` for 404 handling

## Component Architecture

### Component Organization
- Create reusable components in the `components/` directory
- Use feature-based grouping (auth/, task/, etc.)
- Implement generic UI components in `components/ui/`
- Follow the container/presentational pattern where appropriate
- Use TypeScript interfaces for component props

### Component Best Practices
- Use TypeScript for all components
- Implement proper prop validation
- Use React hooks appropriately
- Follow accessibility best practices (WCAG 2.1 AA)
- Implement responsive design with Tailwind CSS
- Use semantic HTML elements

## API Client Implementation

### Service Layer
- Create dedicated service files for API interactions
- Implement proper error handling
- Use TypeScript interfaces for request/response types
- Handle loading and error states
- Implement request/response interceptors if needed

### Authentication Integration
- Attach JWT tokens to all authenticated requests
- Use Authorization: Bearer {token} header format
- Handle token expiration and refresh
- Redirect to login on authentication failures
- Store tokens securely (preferably in httpOnly cookies or secure local storage)

### Request/Response Handling
- Implement proper request validation
- Handle different HTTP status codes appropriately
- Use async/await for API calls
- Implement proper error messaging
- Add loading states during API operations

## Styling Conventions

### Tailwind CSS Usage
- Use Tailwind utility classes for styling
- Implement responsive design with Tailwind breakpoints
- Use consistent color palette and spacing scale
- Create reusable component classes
- Follow mobile-first responsive approach

### Design System
- Maintain consistent spacing using Tailwind's spacing scale
- Use consistent typography scales
- Implement consistent color naming
- Create reusable component variants
- Document design patterns and components

## TypeScript Conventions

### Type Definitions
- Create TypeScript interfaces for all data structures
- Use strict typing throughout the application
- Implement proper error types
- Use generics where appropriate
- Create utility types for common patterns

### Type Safety
- Enable strict mode in TypeScript configuration
- Use React's built-in types (React.FC, React.ReactNode, etc.)
- Implement proper null/undefined handling
- Use discriminated unions for complex types
- Validate API responses with Zod or similar libraries

## Authentication Handling

### JWT Token Management
- Securely store JWT tokens (preferably in httpOnly cookies)
- Attach tokens to authenticated API requests
- Handle token expiration gracefully
- Implement token refresh mechanisms
- Clear tokens on logout

### Protected Routes
- Create higher-order components or hooks for protected routes
- Redirect unauthenticated users to login
- Show appropriate loading states during auth checks
- Implement role-based access control if needed
- Handle authentication state globally

### Session Management
- Maintain authentication state across the app
- Implement proper logout functionality
- Handle concurrent sessions appropriately
- Clear sensitive data on session end
- Implement session timeout handling

## Performance Optimization

### Code Splitting
- Use Next.js automatic code splitting
- Implement dynamic imports for non-critical components
- Use React.lazy and Suspense for route-level splitting
- Implement component-level code splitting where appropriate

### Image Optimization
- Use Next.js Image component for all images
- Implement proper image sizing and formats
- Use WebP or AVIF formats when possible
- Implement lazy loading for below-fold images

### Caching
- Implement HTTP caching headers
- Use Next.js caching strategies
- Implement client-side caching where appropriate
- Use React.memo for component optimization
- Implement proper data fetching caching

## Testing Guidelines

### Component Testing
- Use React Testing Library for component tests
- Write tests for user interactions
- Test accessibility features
- Test error states and edge cases
- Use Jest for utility function tests

### Integration Testing
- Test API integration flows
- Test authentication flows
- Test form submissions
- Test navigation between pages
- Test responsive behavior

## Accessibility Guidelines

### WCAG Compliance
- Follow WCAG 2.1 AA standards
- Use semantic HTML elements
- Implement proper ARIA attributes
- Ensure keyboard navigation works properly
- Provide alternative text for images

### Screen Reader Support
- Use proper heading hierarchy
- Implement skip navigation links
- Use ARIA landmarks appropriately
- Test with screen readers
- Provide sufficient color contrast

## Development Guidelines

### Code Organization
- Follow Next.js best practices for file structure
- Use consistent naming conventions
- Separate concerns appropriately
- Implement proper error boundaries
- Use Next.js built-in features effectively

### State Management
- Use React state for component-level state
- Use Context API for global state
- Consider external libraries for complex state (Redux Toolkit, Zustand)
- Implement proper state update patterns
- Avoid unnecessary re-renders

### Security
- Sanitize user inputs on the client side
- Implement proper error handling
- Avoid exposing sensitive data in client-side code
- Use HTTPS in production
- Implement Content Security Policy headers

## Spec-Driven Development

### Agentic Development Constraints
- All code must be AI-generated based on specifications
- Follow spec-driven development methodology
- No manual coding allowed - use skill agents
- Ensure all functionality matches feature specifications
- Maintain traceability from specs to implementation

### Implementation Workflow
1. Generate specification from feature requirements
2. Create implementation plan based on spec
3. Generate tasks from plan
4. Execute with appropriate skill agents
5. Verify implementation matches specification

## Responsive Design

### Breakpoints
- Use Tailwind's default breakpoints (sm, md, lg, xl, 2xl)
- Implement mobile-first design approach
- Test on various screen sizes
- Consider touch targets for mobile devices
- Optimize for different device orientations

### Responsive Patterns
- Use responsive utility classes
- Implement flexible grid layouts
- Adjust typography for different screens
- Optimize navigation for mobile
- Consider performance on mobile devices

This CLAUDE.md file serves as the authoritative guide for frontend development in Phase-2, ensuring consistency and adherence to project standards while following spec-driven, agentic development principles.