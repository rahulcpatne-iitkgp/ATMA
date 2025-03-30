function showToast(message, type = 'success', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  
  document.body.appendChild(toast);
  
  // Force reflow to enable animation
  toast.offsetHeight;
  
  toast.classList.add('show');
  
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 300);
  }, duration);
}

// Listen for HTMX events
document.addEventListener('htmx:afterSwap', function(event) {
  if (event.detail.target.matches('.htmx-message')) {
    const messageType = event.detail.target.dataset.messageType || 'success';
    showToast(event.detail.target.innerText, messageType);
  }
});