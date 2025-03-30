document.addEventListener('DOMContentLoaded', function() {
  // Handle checkbox items
  const checkboxItems = document.querySelectorAll('.checkbox-item');
  
  checkboxItems.forEach(item => {
    // Set initial state
    const checkbox = item.querySelector('input[type="checkbox"]');
    if (checkbox.checked) {
      item.classList.add('selected');
    }
    
    // Add click event to entire item
    item.addEventListener('click', function(e) {
      // If click wasn't on the checkbox itself
      if (e.target.tagName !== 'INPUT') {
        checkbox.checked = !checkbox.checked;
        
        // Toggle selected class
        this.classList.toggle('selected', checkbox.checked);
        
        // Trigger change event
        const event = new Event('change');
        checkbox.dispatchEvent(event);
      }
    });
    
    // Update selected state when checkbox changes
    checkbox.addEventListener('change', function() {
      item.classList.toggle('selected', this.checked);
    });
  });
});