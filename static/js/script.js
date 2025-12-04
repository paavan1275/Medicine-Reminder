// Medication Reminder App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }

    // Check for reminders every 10 seconds
    setInterval(checkReminders, 10000);
    // Also check immediately on page load
    checkReminders();
});

// Create and show popup notification
function showPopupNotification(reminder) {
    const notificationDiv = document.createElement('div');
    notificationDiv.className = 'notification-popup';
    notificationDiv.innerHTML = `
        <div class="notification-content">
            <div class="notification-header">
                <span class="notification-title">💊 Time to Take Your Medication</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="notification-body">
                <p class="med-name"><strong>${reminder.medication_name}</strong></p>
                <p class="med-dosage">${reminder.dosage}</p>
                <p class="med-time">Scheduled at ${reminder.time}</p>
            </div>
            <div class="notification-actions">
                <button class="notification-btn notification-btn-success" onclick="logDoseFromNotification(${reminder.medication_id}); this.parentElement.parentElement.parentElement.remove();">
                    ✓ Mark as Taken
                </button>
                <button class="notification-btn notification-btn-secondary" onclick="this.parentElement.parentElement.parentElement.remove();">
                    Remind Later
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(notificationDiv);
    
    // Play notification sound
    playNotificationSound();
    
    // Auto-remove after 10 seconds if not interacted
    setTimeout(function() {
        if (notificationDiv.parentElement) {
            notificationDiv.remove();
        }
    }, 10000);
}

// Check if any reminders are due - with minute and second precision
async function checkReminders() {
    try {
        const response = await fetch('/api/upcoming-reminders');
        if (!response.ok) return;
        
        const reminders = await response.json();
        
        const now = new Date();
        const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
        const currentSecond = now.getSeconds();
        
        reminders.forEach(reminder => {
            // Check if we're within the reminder minute (0-59 seconds)
            if (reminder.time === currentTime) {
                // Only show notification once per minute (when seconds are between 0-10)
                if (currentSecond >= 0 && currentSecond <= 10) {
                    // Check if we haven't shown this notification already
                    const notificationKey = `notif_${reminder.medication_id}_${currentTime}`;
                    if (!sessionStorage.getItem(notificationKey)) {
                        showPopupNotification(reminder);
                        showBrowserNotification(reminder);
                        // Mark that we've shown this notification
                        sessionStorage.setItem(notificationKey, 'shown');
                        // Clear the flag after 55 seconds so it can trigger again next minute
                        setTimeout(() => {
                            sessionStorage.removeItem(notificationKey);
                        }, 55000);
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error checking reminders:', error);
    }
}

// Show browser notification
function showBrowserNotification(reminder) {
    if ('Notification' in window && Notification.permission === 'granted') {
        const notification = new Notification('💊 Time to Take Your Medication', {
            body: `${reminder.medication_name} - ${reminder.dosage}`,
            icon: '💊',
            tag: `med-${reminder.medication_id}`,
            requireInteraction: true,
            badge: '💊'
        });

        notification.onclick = function() {
            window.focus();
            notification.close();
        };
    }
}

// Play notification sound
function playNotificationSound() {
    // Create a simple beep sound using Web Audio API
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
}

// Log dose from notification popup
async function logDoseFromNotification(medicationId) {
    try {
        const response = await fetch(`/api/dose/${medicationId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            showSuccessToast(data.message);
        } else {
            showErrorToast('Error logging dose');
        }
    } catch (error) {
        console.error('Error:', error);
        showErrorToast('Error logging dose');
    }
}

// Form validation
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    
    for (let field of requiredFields) {
        if (!field.value.trim()) {
            alert(`${field.labels[0].textContent} is required!`);
            field.focus();
            return false;
        }
    }
    
    return true;
}

// Show success toast notification
function showSuccessToast(message) {
    showToast(message, 'success');
}

// Show error toast notification
function showErrorToast(message) {
    showToast(message, 'error');
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add dose via AJAX
async function logDoseQuick(medicationId) {
    try {
        const response = await fetch(`/api/dose/${medicationId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            showSuccessToast(data.message);
            location.reload();
        } else {
            showErrorToast('Error logging dose');
        }
    } catch (error) {
        console.error('Error:', error);
        showErrorToast('Error logging dose');
    }
}

// Auto-hide alerts after 5 seconds
setTimeout(function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}, 100);

