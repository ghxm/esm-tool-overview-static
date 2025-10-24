// Enhanced List.js functionality
document.addEventListener('DOMContentLoaded', function() {
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Focus search on Ctrl/Cmd + F
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            const searchInput = document.getElementById('search');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // Clear search on Escape
        if (e.key === 'Escape') {
            const searchInput = document.getElementById('search');
            const categoryFilter = document.getElementById('category-filter');
            
            if (searchInput && searchInput.value) {
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('keyup'));
            }
            
            if (categoryFilter && categoryFilter.value) {
                categoryFilter.value = '';
                categoryFilter.dispatchEvent(new Event('change'));
            }
        }
    });
    
    // Add loading state for external links
    document.addEventListener('click', function(e) {
        if (e.target && e.target.matches && e.target.matches('a[target="_blank"]')) {
            const link = e.target;
            const originalText = link.textContent;
            
            link.textContent = '...';
            setTimeout(() => {
                link.textContent = originalText;
            }, 1000);
        }
    });
    
    // Add tooltips to truncated content
    document.addEventListener('mouseenter', function(e) {
        if (e.target && e.target.matches && e.target.matches('td')) {
            const cell = e.target;
            if (cell.scrollWidth > cell.clientWidth) {
                cell.title = cell.textContent.trim();
            }
        }
    }, true);
    
    // Enhanced sorting indicators
    document.querySelectorAll('.sort').forEach(function(header) {
        header.addEventListener('click', function() {
            // Visual feedback for sorting
            document.querySelectorAll('.sort').forEach(h => h.classList.remove('sort-active'));
            this.classList.add('sort-active');
        });
    });
});