# Flask to FastAPI + Vue.js Migration Plan

This plan outlines the comprehensive migration of the weekend overtime management system from Flask to a modern FastAPI backend with Vue.js frontend, preserving all existing functionality including department isolation, real-time status updates, and Chinese timezone support.

## Current Architecture Analysis

The existing Flask application includes:
- **Backend**: Flask 3.1.2 with SQLite database (WAL mode for concurrency)
- **Frontend**: Server-side rendered Jinja2 templates with vanilla JavaScript
- **Database**: SQLite with normalized schema (departments, sub_departments, staffs, sat/sun tables)
- **Core Features**:
  - Department-based access control with 1-year cookie persistence
  - Staff management with sub-department support
  - Real-time overtime status toggling (bg-1: none, bg-2: internal, bg-3: business trip)
  - Batch operations (clear all, set all internal, set all business trip)
  - Chinese timezone support (Asia/Shanghai)
  - Comprehensive info page showing all departments' overtime status
  - Mobile-responsive design with grid layout

### Current Route Structure
- `/` - Main management interface (index)
- `/select-department` - Department selection page
- `/edit-names` - Staff add/remove operations
- `/toggle-sat` - AJAX endpoint for status changes
- `/info` - Cross-department overtime statistics

### Key Technical Details
- Status tokens: bg-1 (default/white), bg-2 (overtime/yellow), bg-3 (business trip/blue)
- Department isolation enforced via cookie validation
- Optimistic UI updates with error rollback
- Parameterized queries for SQL injection prevention
- Defensive programming with exception handling

## Migration Strategy

### Phase 1: Backend Migration (Flask → FastAPI)

#### 1.1 Project Structure Reorganization
```
weekend-overtime/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── database.py     # Database connection and configuration
│   │   ├── models/         # Pydantic models
│   │   ├── routers/        # API route handlers
│   │   └── middleware.py   # CORS and other middleware
│   ├── requirements.txt
│   └── alembic/           # Database migrations (optional)
├── frontend/               # Vue.js application
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/        # Pinia state management
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
└── database/              # Shared database files
    └── weekend-overtime.sqlite
```

#### 1.2 FastAPI Backend Implementation
- **Database Layer**: Keep existing SQLite database, add SQLAlchemy ORM
- **API Endpoints**: Convert Flask routes to FastAPI routers
  - `GET /api/departments` - List all departments
  - `POST /api/departments/select` - Set department cookie (1-year expiry)
  - `GET /api/staffs` - Get staff by department with sub-department info
  - `POST /api/staffs` - Add/remove staff with sub-department support
  - `POST /api/overtime/toggle` - Toggle overtime status (bg-1/bg-2/bg-3)
  - `GET /api/overtime/status` - Get current overtime status by day
  - `GET /api/info/statistics` - Cross-department overtime statistics
- **Authentication**: Maintain department-based access control via cookies
- **CORS**: Enable cross-origin requests for Vue.js frontend
- **Timezone**: Preserve Asia/Shanghai timezone handling
- **Validation**: Use Pydantic models for input validation

#### 1.3 API Response Standards
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed"
}
```

### Phase 2: Frontend Migration (Templates → Vue.js)

#### 2.1 Vue.js Application Setup
- **Framework**: Vue 3 with Composition API
- **Build Tool**: Vite for fast development
- **State Management**: Pinia for department and staff state
- **Routing**: Vue Router for SPA navigation
- **UI Framework**: Element Plus or similar for consistent design
- **HTTP Client**: Axios for API communication

#### 2.2 Component Architecture
```
src/
├── components/
│   ├── StaffList.vue        # Staff management interface
│   ├── DepartmentSelector.vue # Department selection
│   ├── OvertimeToggle.vue   # Individual staff status toggle
│   └── BatchOperations.vue  # Bulk operations
├── views/
│   ├── Home.vue            # Main management interface
│   ├── DepartmentSelect.vue # Department selection page
│   └── Info.vue            # Statistics view
├── stores/
│   ├── department.js       # Department state
│   └── staff.js           # Staff and overtime state
└── utils/
    └── api.js              # API client configuration
```

#### 2.3 Feature Implementation
- **Department Management**: Cookie-based department selection with 1-year persistence
- **Staff Management**: Real-time add/remove with sub-department support and optimistic updates
- **Overtime Status**: Click-to-cycle status (bg-1 → bg-2 → bg-3 → bg-1) with color coding
- **Batch Operations**: 
  - Clear all overtime (set to bg-1)
  - Set all to internal overtime (bg-2)
  - Set all to business trip (bg-3)
- **Real-time Updates**: Optimistic UI updates with server synchronization and error rollback
- **Mobile Responsiveness**: Preserve existing grid layout (10→6→4→3 columns based on screen size)
- **Chinese Timezone**: Maintain Asia/Shanghai timezone for info page
- **Cross-department View**: Info page showing all departments' overtime status

### Phase 3: Integration and Testing

#### 3.1 Development Environment
- **Backend Development**: `uvicorn backend.app.main:app --reload`
- **Frontend Development**: `npm run dev` with Vite proxy to backend
- **Database**: Shared SQLite instance for both development and production

#### 3.2 Migration Validation
- **Functional Testing**: Ensure all existing features work identically
- **Performance Testing**: Verify response times and concurrent user support
- **Browser Compatibility**: Test across modern browsers
- **Mobile Responsiveness**: Ensure mobile-friendly interface

## Technical Implementation Details

### Database Layer
- **Preserve Schema**: Keep existing SQLite schema unchanged (departments, sub_departments, staffs, sat, sun, presets_* tables)
- **WAL Mode**: Maintain WAL journal mode for concurrency
- **Connection Management**: Use SQLAlchemy with connection pooling
- **Security**: Continue using parameterized queries via SQLAlchemy ORM
- **Timezone**: Preserve Asia/Shanghai timezone handling for info page

### API Design Principles
- **RESTful Design**: Follow HTTP standards and REST conventions
- **Consistent Responses**: Standardized JSON response format
- **Error Handling**: Comprehensive error responses with proper HTTP status codes
- **Input Validation**: Pydantic models for request/response validation
- **Cookie Management**: Maintain department cookie with 1-year expiry
- **CORS Configuration**: Proper CORS setup for Vue.js frontend

### Frontend Architecture
- **Component-Based**: Modular Vue 3 components with Composition API
- **State Management**: Pinia for reactive state management
- **Routing**: Vue Router for SPA navigation
- **HTTP Client**: Axios with interceptors for API calls
- **Optimistic Updates**: Client-side updates with server synchronization
- **Error Handling**: Graceful error handling with user feedback
- **Mobile-First**: Responsive design preserving existing breakpoints

### Security Considerations
- **Department Isolation**: Maintain strict department-based access control
- **Input Validation**: Both client and server-side validation
- **SQL Injection Prevention**: Continue using parameterized queries
- **Cookie Security**: Secure cookie configuration for department selection
- **CORS Security**: Proper CORS configuration to prevent unauthorized access

## Deployment Strategy

### Development Deployment
- Backend: FastAPI development server
- Frontend: Vite development server with proxy
- Database: Local SQLite file

### Production Deployment
- Backend: Gunicorn + Uvicorn workers
- Frontend: Static files served by Nginx
- Database: SQLite with regular backups
- Reverse Proxy: Nginx for SSL termination and static file serving

## Git Strategy and Version Control

### Current Repository Status
- **Branch**: main (ahead of origin/main by 1 commit)
- **Remote**: git@github.com:wlhd7/dz-weekend-overtime.git
- **Latest Tag**: v0.0.1
- **Working Tree**: Clean (no uncommitted changes)

### Recommended Git Workflow

### Chosen Git Strategy: Branch-Based Migration

**Selected Approach**: Option 1 - Branch-Based Migration
- **Reasoning**: Direct control over repository, simpler workflow for this project
- **Implementation**: Create `feature/fastapi-vue-migration` branch for all migration work

#### Pre-Migration Git Steps
```bash
# 1. Push current unpushed commit
git push origin main

# 2. Create backup tag
git tag v0.0.1-backup
git push origin v0.0.1-backup

# 3. Create migration branch
git checkout -b feature/fastapi-vue-migration

# 4. Begin migration work...
```

#### Migration Commit Plan
1. **Initial Structure**: `feat: add FastAPI backend and Vue.js frontend structure`
2. **Backend API**: `feat: implement FastAPI endpoints for all Flask routes`
3. **Frontend Components**: `feat: create Vue.js components matching existing UI`
4. **Integration**: `feat: integrate frontend with backend APIs`
5. **Testing**: `test: comprehensive testing and bug fixes`
6. **Documentation**: `docs: update README and deployment instructions`

#### Post-Migration Git Steps
```bash
# 1. Merge to main
git checkout main
git merge feature/fastapi-vue-migration

# 2. Tag new version
git tag v1.0.0
git push origin main --tags

# 3. Clean up (optional)
git branch -d feature/fastapi-vue-migration
```

### Migration Commits Strategy
- **Atomic Commits**: Each logical change in separate commit
- **Clear Messages**: Use conventional commit format (feat:, fix:, refactor:)
- **Version Tags**: Tag v1.0.0 when migration is complete
- **Backup Points**: Create tags at major milestones

### Backup and Rollback Plan
- **Pre-Migration Tag**: Create `v0.0.1-backup` before starting
- **Branch Protection**: Keep main branch stable during migration
- **Rollback Strategy**: Ability to revert to v0.0.1 if needed

## Risk Mitigation

### Data Migration
- **Zero-Downtime**: Gradual migration approach with parallel running
- **Schema Preservation**: No database schema changes required
- **Backup Strategy**: Full database backup before migration
- **Rollback Plan**: Ability to revert to Flask version if needed

### Feature Parity Validation
- **Comprehensive Testing**: Detailed test cases for all existing features
- **UI Consistency**: Preserve exact visual design and interactions
- **Performance Benchmarks**: Ensure no performance degradation
- **Mobile Compatibility**: Test responsive design across devices
- **Browser Testing**: Cross-browser compatibility verification

### Technical Risks
- **Cookie Management**: Ensure department isolation works correctly
- **Real-time Updates**: Maintain optimistic update behavior
- **Error Handling**: Preserve all error handling and rollback mechanisms
- **Timezone Handling**: Maintain Asia/Shanghai timezone support
- **Concurrent Access**: Preserve WAL mode benefits for multiple users

## Timeline Estimate

- **Phase 1 (Backend)**: 3-4 days
- **Phase 2 (Frontend)**: 4-5 days  
- **Phase 3 (Integration)**: 2-3 days
- **Testing & Bug Fixes**: 2-3 days
- **Total**: 11-15 days

## Success Criteria

1. **Complete Feature Preservation**: All existing functionality works identically
2. **Department Security**: Strict department isolation maintained
3. **Real-time Performance**: Optimistic updates and error rollback preserved
4. **Mobile Experience**: Responsive design maintained across all screen sizes
5. **Chinese Timezone**: Asia/Shanghai timezone support fully functional
6. **Data Integrity**: Zero data loss during migration
7. **User Experience**: Seamless transition with improved performance
8. **Maintainability**: Modern codebase with better developer experience
