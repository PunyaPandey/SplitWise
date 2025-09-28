document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle split type changes
    const splitTypeSelect = document.getElementById('split_type');
    const splitDetails = document.getElementById('split-details');
    
    if (splitTypeSelect && splitDetails) {
        splitTypeSelect.addEventListener('change', updateSplitDetails);
        updateSplitDetails(); // Initialize on page load
    }

    function updateSplitDetails() {
        const splitType = splitTypeSelect.value;
        let html = '';
        
        // Get all users (excluding the payer)
        const paidBy = document.getElementById('paid_by');
        const payerId = paidBy ? paidBy.value : null;
        
        // Get all user options
        const userOptions = document.querySelectorAll('#paid_by option');
        
        switch(splitType) {
            case 'EQUAL':
                // For equal split, we don't need additional inputs
                html = `
                    <div class="alert alert-info mt-3">
                        <i class="bi bi-info-circle"></i> The expense will be split equally among all participants.
                    </div>
                `;
                break;
                
            case 'EXACT':
                html = `
                    <div class="mt-3">
                        <h5>Enter exact amounts</h5>
                        <div class="mb-3">
                            <label class="form-label">Amounts per person</label>
                            ${Array.from(userOptions)
                                .filter(opt => opt.value !== payerId)
                                .map(opt => `
                                    <div class="input-group mb-2">
                                        <span class="input-group-text">${opt.textContent}</span>
                                        <input type="number" step="0.01" class="form-control" name="exact_${opt.value}" placeholder="0.00">
                                        <span class="input-group-text">$</span>
                                    </div>
                                `).join('')}
                        </div>
                    </div>
                `;
                break;
                
            case 'PERCENTAGE':
                html = `
                    <div class="mt-3">
                        <h5>Enter percentages</h5>
                        <div class="mb-3">
                            <label class="form-label">Percentage per person (must total 100%)</label>
                            ${Array.from(userOptions)
                                .filter(opt => opt.value !== payerId)
                                .map(opt => `
                                    <div class="input-group mb-2">
                                        <span class="input-group-text">${opt.textContent}</span>
                                        <input type="number" step="0.1" class="form-control percentage-input" name="percent_${opt.value}" placeholder="0.0">
                                        <span class="input-group-text">%</span>
                                    </div>
                                `).join('')}
                            <div class="form-text">Total: <span id="percentage-total">0</span>%</div>
                        </div>
                    </div>
                `;
                
                // Add event listener for percentage inputs
                setTimeout(() => {
                    const percentageInputs = document.querySelectorAll('.percentage-input');
                    percentageInputs.forEach(input => {
                        input.addEventListener('input', updatePercentageTotal);
                    });
                }, 0);
                break;
        }
        
        splitDetails.innerHTML = html;
    }
    
    function updatePercentageTotal() {
        const percentageInputs = document.querySelectorAll('.percentage-input');
        let total = 0;
        
        percentageInputs.forEach(input => {
            total += parseFloat(input.value) || 0;
        });
        
        const totalElement = document.getElementById('percentage-total');
        if (totalElement) {
            totalElement.textContent = total.toFixed(1);
            
            // Add warning if total is not 100%
            if (Math.abs(total - 100) > 0.1) {
                totalElement.classList.add('text-danger');
                totalElement.classList.remove('text-success');
            } else {
                totalElement.classList.remove('text-danger');
                totalElement.classList.add('text-success');
            }
        }
    }
    
    // Handle form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Auto-format currency inputs
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !isNaN(this.value)) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });
});
