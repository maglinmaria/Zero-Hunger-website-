# Overview

Zero Hunger is a Flask web application designed to connect food providers (restaurants, hotels, households) with receivers (NGOs, shelters, customers) to reduce food waste and fight hunger. The platform allows providers to upload surplus food with photos and details, while receivers can browse and request available food items based on location and category. Users can dynamically switch between provider and receiver roles through their profile.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Application Structure
The application follows a modular Flask blueprint architecture with clear separation of concerns:

- **Main Application** (`app.py`): Centralized Flask app configuration with session management, file upload settings, and blueprint registration
- **Modular Blueprints**: Separate blueprints for authentication (`auth/`), provider functionality (`provider/`), and receiver functionality (`receiver/`)
- **Data Models** (`models.py`): In-memory data storage using Python dictionaries with UUID-based unique identifiers
- **Template Organization**: Structured HTML templates using Jinja2 with a base template and role-specific subdirectories

## Authentication & Authorization
- **Flask-Login Integration**: Session-based user authentication with role-based access control
- **Password Security**: Werkzeug password hashing for secure credential storage
- **Role Management**: Dynamic role switching between 'provider' and 'receiver' with different dashboard views and permissions

## Data Storage Design
- **In-Memory MVP Approach**: Uses Python dictionaries for rapid prototyping and development
- **Entity Models**: User, Food, and FoodRequest classes with proper relationships
- **UUID Identification**: All entities use UUID4 for unique identification to avoid conflicts

## Frontend Architecture
- **Bootstrap Dark Theme**: Consistent UI using Bootstrap 5 with dark theme support
- **Responsive Design**: Mobile-first approach with responsive grid layouts
- **Component Organization**: Reusable templates with extends/include patterns
- **Client-Side Enhancements**: JavaScript for form validation, image preview, and UX improvements

## File Management System
- **Image Upload Handling**: Secure file upload with extension validation and filename sanitization
- **Static Asset Organization**: Structured static files with separate CSS, JS, and upload directories
- **Image Processing**: Built-in support for multiple image formats with size constraints

## Business Logic Patterns
- **Role-Based Workflows**: Different user journeys for providers (upload, manage) vs receivers (browse, request)
- **Status Management**: Food items have status tracking (available, booked, completed)
- **Location-Based Matching**: Simple pin code-based location filtering system
- **Time-Based Food Management**: Expiry hour tracking for food freshness

# External Dependencies

## Core Framework Stack
- **Flask**: Primary web framework with Werkzeug WSGI utilities
- **Flask-Login**: User session management and authentication
- **Jinja2**: Template engine (included with Flask)

## Frontend Libraries
- **Bootstrap 5**: CSS framework with dark theme variant from Replit CDN
- **Font Awesome 6.4.0**: Icon library from Cloudflare CDN
- **Bootstrap JavaScript**: Client-side components and interactions

## File Processing
- **Werkzeug**: Secure filename handling and file upload utilities
- **PIL/Pillow**: Image processing capabilities (referenced for future AI integration)

## Development & Deployment
- **Python Standard Library**: UUID, datetime, os, logging modules
- **Replit Environment**: Configured for Replit hosting with ProxyFix middleware

## Future Integration Points
- **TensorFlow/Keras**: Planned AI food image recognition system
- **Database Migration Path**: Architecture supports easy transition from in-memory to persistent storage
- **Geolocation Services**: Framework ready for enhanced location services beyond pin codes