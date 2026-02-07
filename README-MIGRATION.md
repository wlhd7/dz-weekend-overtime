# FastAPI + Vue.js Migration

## Development Setup

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Database Setup
The application uses the existing SQLite database. Make sure `database/weekend-overtime.sqlite` exists.

## Architecture

- **Backend**: FastAPI with SQLAlchemy ORM
- **Frontend**: Vue 3 + Pinia + Element Plus
- **Database**: SQLite (existing schema preserved)
- **API**: RESTful endpoints with proper error handling

## API Endpoints

### Departments
- `GET /api/departments` - List all departments
- `GET /api/departments/current` - Get current department from cookie
- `POST /api/departments/select` - Set department cookie

### Staffs
- `GET /api/staffs` - Get staff by department
- `GET /api/staffs/sub-departments` - Get sub-departments
- `POST /api/staffs/add` - Add staff
- `POST /api/staffs/remove` - Remove staff

### Overtime
- `POST /api/overtime/toggle` - Toggle staff status
- `GET /api/overtime/status` - Get overtime status

### Info
- `GET /api/info/statistics` - Get cross-department statistics

## Status Tokens
- `bg-1`: No overtime (white)
- `bg-2`: Internal overtime (yellow)
- `bg-3`: Business trip (blue)

## Migration Status

✅ Backend API implementation
✅ Frontend Vue.js components
✅ Database schema preservation
⏳ Integration testing
⏳ Bug fixes and optimization
⏳ Production deployment setup
