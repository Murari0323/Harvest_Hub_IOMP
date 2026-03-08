/**
 * HarvestHub — Client-side JavaScript
 * ====================================
 * Handles: delete confirmations, search filtering, form validation hints.
 */

document.addEventListener('DOMContentLoaded', function () {

    // ── 1. Confirm before deleting a crop ──────────────────────
    document.querySelectorAll('.delete-form').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!confirm('Are you sure you want to delete this crop?')) {
                e.preventDefault();
            }
        });
    });

    // ── 2. Auto-dismiss flash alerts after 5 seconds ──────────
    document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // ── 3. Quantity validation on cart (cannot exceed max) ─────
    var qtyInput = document.getElementById('quantity');
    if (qtyInput && qtyInput.hasAttribute('max')) {
        qtyInput.addEventListener('change', function () {
            var max = parseFloat(this.getAttribute('max'));
            if (parseFloat(this.value) > max) {
                this.value = max;
                alert('Maximum available quantity is ' + max + ' kg');
            }
            if (parseFloat(this.value) <= 0) {
                this.value = 1;
            }
        });
    }

    // ── 4. Live search filter on marketplace (optional) ───────
    var searchInput = document.getElementById('searchInput');
    var cropGrid = document.getElementById('cropGrid');
    if (searchInput && cropGrid) {
        searchInput.addEventListener('input', function () {
            var query = this.value.toLowerCase();
            cropGrid.querySelectorAll('.crop-card-col').forEach(function (col) {
                var text = col.textContent.toLowerCase();
                col.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }
});
