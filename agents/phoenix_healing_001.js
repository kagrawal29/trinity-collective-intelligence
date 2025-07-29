// PHOENIX HEALING PROTOCOL - Form State Preservation
// Transforms USER RAGE 10 → 0

const FormHealing = {
  init() {
    // 1. AUTO-SAVE every 5 seconds + on blur
    this.attachAutoSave();
    
    // 2. PRESERVE on validation error
    this.preserveOnError();
    
    // 3. VISUAL REASSURANCE
    this.showSaveIndicator();
  },
  
  attachAutoSave() {
    const fields = form.querySelectorAll('input, textarea, select');
    const saveState = () => {
      const data = new FormData(form);
      localStorage.setItem('registration_draft', JSON.stringify(Object.fromEntries(data)));
      this.flash('✨ Saved', 1000);
    };
    
    // Save on change with debounce
    fields.forEach(field => {
      field.addEventListener('input', debounce(saveState, 5000));
      field.addEventListener('blur', saveState);
    });
  },
  
  preserveOnError() {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      
      try {
        await submitForm(formData);
        // Clear saved data only on success
        localStorage.removeItem('registration_draft');
      } catch (error) {
        // CRITICAL: Restore all values on error
        this.restoreFromStorage();
        this.showHelpfulError(error);
      }
    });
  },
  
  restoreFromStorage() {
    const saved = localStorage.getItem('registration_draft');
    if (saved) {
      const data = JSON.parse(saved);
      Object.entries(data).forEach(([name, value]) => {
        const field = form.elements[name];
        if (field) field.value = value;
      });
      this.flash('✨ Your work is restored!', 2000);
    }
  },
  
  showHelpfulError(error) {
    // Transform cryptic errors to helpful guidance
    const messages = {
      'INVALID_PHONE_FORMAT': 'Phone number needs format: 555-123-4567',
      'EMAIL_INVALID': 'Email should look like: name@example.com'
    };
    
    const helpfulMessage = messages[error.code] || error.message;
    this.showError(helpfulMessage, {
      icon: '💡',
      suggestion: true
    });
  },
  
  flash(message, duration = 1000) {
    const indicator = document.createElement('div');
    indicator.className = 'save-indicator';
    indicator.textContent = message;
    indicator.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #10b981;
      color: white;
      padding: 8px 16px;
      border-radius: 6px;
      animation: fadeIn 0.3s ease;
    `;
    document.body.appendChild(indicator);
    setTimeout(() => indicator.remove(), duration);
  }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  FormHealing.init();
  // Check for saved data on load
  FormHealing.restoreFromStorage();
});