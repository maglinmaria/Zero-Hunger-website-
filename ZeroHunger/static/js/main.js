// Main JavaScript file for Zero Hunger app

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap tooltips are used
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-important)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // File upload preview
    const imageInput = document.getElementById('image');
    if (imageInput) {
        imageInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Create preview if doesn't exist
                    let preview = document.getElementById('image-preview');
                    if (!preview) {
                        preview = document.createElement('div');
                        preview.id = 'image-preview';
                        preview.className = 'mt-2';
                        imageInput.parentNode.appendChild(preview);
                    }
                    
                    preview.innerHTML = `
                        <img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px; max-height: 200px;" alt="Preview">
                        <p class="small text-muted mt-1">Preview: ${file.name}</p>
                    `;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Confirm actions for important buttons
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            const message = button.getAttribute('data-confirm');
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });

    // Auto-refresh for time-sensitive content (expiry times)
    const timeElements = document.querySelectorAll('[data-expiry]');
    if (timeElements.length > 0) {
        setInterval(function() {
            timeElements.forEach(function(element) {
                const expiryTime = parseInt(element.getAttribute('data-expiry'));
                const currentTime = Math.floor(Date.now() / 1000);
                const hoursLeft = Math.max(0, Math.floor((expiryTime - currentTime) / 3600));
                
                element.textContent = hoursLeft + 'h left';
                
                // Update styling based on time left
                element.className = element.className.replace(/text-\w+/, '');
                if (hoursLeft <= 2) {
                    element.classList.add('text-danger');
                } else if (hoursLeft <= 6) {
                    element.classList.add('text-warning');
                } else {
                    element.classList.add('text-success');
                }
            });
        }, 60000); // Update every minute
    }

    // Search functionality enhancement
    const searchInput = document.querySelector('input[name="location"]');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                // Optional: Implement real-time search suggestions
                console.log('Search for:', searchInput.value);
            }, 300);
        });
    }

    // Role switching confirmation
    const roleSwitchLinks = document.querySelectorAll('a[href*="/switch_role/"]');
    roleSwitchLinks.forEach(function(link) {
        link.addEventListener('click', function(event) {
            const role = link.getAttribute('href').split('/').pop();
            const message = `Are you sure you want to switch to ${role} mode?`;
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });

    // Loading states for forms
    const submitButtons = document.querySelectorAll('form button[type="submit"]');
    submitButtons.forEach(function(button) {
        button.closest('form').addEventListener('submit', function() {
            button.disabled = true;
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            
            // Re-enable after 5 seconds as fallback
            setTimeout(function() {
                button.disabled = false;
                button.innerHTML = originalText;
            }, 5000);
        });
    });
});

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
}

function formatTimeAgo(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInSeconds = Math.floor((now - time) / 1000);
    
    if (diffInSeconds < 60) {
        return 'just now';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
        return time.toLocaleDateString();
    }
}
