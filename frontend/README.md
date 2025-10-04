# Expense Management System - Frontend

A modern React-based frontend for the Expense Management System built for the Odoo Hackathon 2025.

## Features

### 🏢 Admin Features
- **Company Setup**: Create company accounts with admin signup
- **User Management**: Create, manage, and assign roles to users
- **Request Oversight**: View all expense requests across the company
- **Rule Creation**: Create custom approval rules for different types of expenses
- **Password Management**: Send password reset emails to users

### 👥 Employee Features
- **Request Submission**: Create new expense requests with detailed information
- **Request Tracking**: View all submitted requests and their current status
- **Request Details**: View detailed information about each request in read-only mode
- **Status Monitoring**: Track pending, approved, and rejected requests

### 👨‍💼 Manager Features
- **Approval Dashboard**: Review and approve/reject pending requests
- **Team Overview**: View team expense statistics
- **Request Details**: Access detailed request information for informed decisions
- **Dual Role Support**: Switch between employee and manager views seamlessly

### 🔄 Role Switching
- Users with manager roles can switch between employee and manager views
- Intuitive toggle interface in the top navigation
- Context-aware navigation based on current view

## Technology Stack

- **React 19** - Modern React with latest features
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router DOM** - Client-side routing
- **React Hook Form** - Form handling and validation
- **Lucide React** - Beautiful icon library
- **Axios** - HTTP client for API requests

## Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── Layout.jsx       # Main layout with navigation
│   ├── CreateRequestModal.jsx
│   ├── RequestDetailModal.jsx
│   ├── CreateRuleModal.jsx
│   └── CreateUserModal.jsx
├── pages/               # Page components
│   ├── LandingPage.jsx  # Landing page with role selection
│   ├── auth/           # Authentication pages
│   │   ├── AdminSignin.jsx
│   │   ├── AdminSignup.jsx
│   │   └── UserSignin.jsx
│   ├── employee/       # Employee-specific pages
│   │   └── EmployeeDashboard.jsx
│   ├── manager/        # Manager-specific pages
│   │   └── ManagerDashboard.jsx
│   └── admin/          # Admin-specific pages
│       ├── AdminDashboard.jsx
│       └── AdminUserManagement.jsx
├── App.jsx             # Main app component with routing
└── main.jsx           # App entry point
```

## Getting Started

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:5173`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## API Integration

The frontend integrates with the backend API endpoints defined in the schema:

### Authentication Endpoints
- `POST /admin/signin` - Admin sign in
- `POST /admin/signup` - Admin sign up
- `POST /user/signin` - User sign in

### User Management Endpoints
- `GET /admin/users` - List all users
- `POST /admin/create_user` - Create new user
- `POST /admin/change_role/{user_id}` - Change user role
- `POST /admin/change_manager/{user_id}` - Change user manager
- `POST /admin/send_password/{user_id}` - Send password reset

### Request Management Endpoints
- `GET /user/requests` - Get user's requests
- `POST /user/create_request` - Create new request
- `GET /admin/requests` - Get all requests
- `GET /admin/requests/{request_id}` - Get request details
- `POST /user/approve_request/{request_id}` - Approve request
- `POST /user/reject_request/{request_id}` - Reject request

### Rule Management Endpoints
- `POST /admin/generate_request_rules/{request_id}` - Create approval rule

## Design System

### Color Palette
- **Primary**: Blue tones (#3b82f6, #2563eb, etc.)
- **Secondary**: Gray tones for neutral elements
- **Success**: Green for approved states
- **Warning**: Yellow for pending states
- **Error**: Red for rejected states

### Components
- **Cards**: Consistent card design for content sections
- **Buttons**: Primary, secondary, success, and danger variants
- **Forms**: Consistent input styling with validation
- **Modals**: Overlay modals for forms and details
- **Tables**: Responsive tables with hover states

## Responsive Design

The application is fully responsive and works on:
- Desktop (1024px+)
- Tablet (768px - 1023px)
- Mobile (320px - 767px)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

### Code Style
- ESLint configuration for code quality
- Consistent component structure
- Proper prop validation
- Clean separation of concerns

### State Management
- React hooks for local state
- Context for global state (user authentication)
- Local storage for persistence

## Contributing

1. Follow the existing code style
2. Add proper error handling
3. Include loading states
4. Test on multiple screen sizes
5. Ensure accessibility standards

## License

This project is part of the Odoo Hackathon 2025.