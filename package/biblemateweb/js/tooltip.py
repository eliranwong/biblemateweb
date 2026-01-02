TOOLTIP_JS = '''
<script>
    let currentTooltip = null;
    let tooltipCache = {};
    let tooltipTimeout = null;
    let currentWord = null;
    let showTimeout = null;
    let initialized = false;
    
    async function fetchTooltipData(word) {
        // Check cache first
        if (tooltipCache[word]) {
            return tooltipCache[word];
        }
        
        try {
            const response = await fetch(`/api/tooltip/${encodeURIComponent(word)}`);
            if (response.ok) {
                const data = await response.json();
                tooltipCache[word] = data;
                return data;
            }
        } catch (error) {
            console.error('Error fetching tooltip:', error);
        }
        return null;
    }
    
    function positionTooltip(tooltip, element) {
        // Get element and viewport dimensions
        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        // Margins from viewport edges
        const margin = 10;
        const arrowSize = 10;
        
        // Calculate available space in each direction
        const spaceTop = rect.top;
        const spaceBottom = viewportHeight - rect.bottom;
        const spaceLeft = rect.left;
        const spaceRight = viewportWidth - rect.right;
        
        // Determine best position
        let position = 'top'; // default
        let top, left;
        
        // Remove old arrows
        const oldArrows = tooltip.querySelectorAll('.tooltip-arrow, .tooltip-arrow-border');
        oldArrows.forEach(arrow => arrow.remove());
        
        // Try to position tooltip
        if (spaceTop > tooltipRect.height + arrowSize + margin && spaceTop > spaceBottom) {
            // Position above
            position = 'top';
            top = rect.top - tooltipRect.height - arrowSize;
            left = rect.left + rect.width / 2 - tooltipRect.width / 2;
            
            // Adjust horizontal position if needed
            if (left < margin) {
                left = margin;
            } else if (left + tooltipRect.width > viewportWidth - margin) {
                left = viewportWidth - tooltipRect.width - margin;
            }
            
            // Add arrow pointing down
            const arrowBorder = document.createElement('div');
            arrowBorder.className = 'tooltip-arrow-border arrow-down';
            tooltip.appendChild(arrowBorder);
            
            const arrow = document.createElement('div');
            arrow.className = 'tooltip-arrow arrow-down';
            tooltip.appendChild(arrow);
            
            // Adjust arrow position if tooltip was shifted
            const arrowLeft = rect.left + rect.width / 2 - left;
            arrow.style.left = arrowLeft + 'px';
            arrowBorder.style.left = arrowLeft + 'px';
            
        } else if (spaceBottom > tooltipRect.height + arrowSize + margin) {
            // Position below
            position = 'bottom';
            top = rect.bottom + arrowSize;
            left = rect.left + rect.width / 2 - tooltipRect.width / 2;
            
            // Adjust horizontal position if needed
            if (left < margin) {
                left = margin;
            } else if (left + tooltipRect.width > viewportWidth - margin) {
                left = viewportWidth - tooltipRect.width - margin;
            }
            
            // Add arrow pointing up
            const arrowBorder = document.createElement('div');
            arrowBorder.className = 'tooltip-arrow-border arrow-up';
            tooltip.appendChild(arrowBorder);
            
            const arrow = document.createElement('div');
            arrow.className = 'tooltip-arrow arrow-up';
            tooltip.appendChild(arrow);
            
            // Adjust arrow position if tooltip was shifted
            const arrowLeft = rect.left + rect.width / 2 - left;
            arrow.style.left = arrowLeft + 'px';
            arrowBorder.style.left = arrowLeft + 'px';
            
        } else if (spaceRight > tooltipRect.width + arrowSize + margin && spaceRight > spaceLeft) {
            // Position to the right
            position = 'right';
            top = rect.top + rect.height / 2 - tooltipRect.height / 2;
            left = rect.right + arrowSize;
            
            // Adjust vertical position if needed
            if (top < margin) {
                top = margin;
            } else if (top + tooltipRect.height > viewportHeight - margin) {
                top = viewportHeight - tooltipRect.height - margin;
            }
            
            // Add arrow pointing left
            const arrowBorder = document.createElement('div');
            arrowBorder.className = 'tooltip-arrow-border arrow-left';
            tooltip.appendChild(arrowBorder);
            
            const arrow = document.createElement('div');
            arrow.className = 'tooltip-arrow arrow-left';
            tooltip.appendChild(arrow);
            
            // Adjust arrow position if tooltip was shifted
            const arrowTop = rect.top + rect.height / 2 - top;
            arrow.style.top = arrowTop + 'px';
            arrowBorder.style.top = arrowTop + 'px';
            
        } else {
            // Position to the left
            position = 'left';
            top = rect.top + rect.height / 2 - tooltipRect.height / 2;
            left = rect.left - tooltipRect.width - arrowSize;
            
            // Adjust vertical position if needed
            if (top < margin) {
                top = margin;
            } else if (top + tooltipRect.height > viewportHeight - margin) {
                top = viewportHeight - tooltipRect.height - margin;
            }
            
            // Add arrow pointing right
            const arrowBorder = document.createElement('div');
            arrowBorder.className = 'tooltip-arrow-border arrow-right';
            tooltip.appendChild(arrowBorder);
            
            const arrow = document.createElement('div');
            arrow.className = 'tooltip-arrow arrow-right';
            tooltip.appendChild(arrow);
            
            // Adjust arrow position if tooltip was shifted
            const arrowTop = rect.top + rect.height / 2 - top;
            arrow.style.top = arrowTop + 'px';
            arrowBorder.style.top = arrowTop + 'px';
        }
        
        // Apply position
        tooltip.style.top = top + 'px';
        tooltip.style.left = left + 'px';
        tooltip.className = 'tooltip-content active position-' + position;
    }
    
    async function showTooltip(element, word) {
        // Clear any pending hide timeout
        if (tooltipTimeout) {
            clearTimeout(tooltipTimeout);
            tooltipTimeout = null;
        }
        
        // If it's the same word, just keep showing
        if (currentWord === word && currentTooltip === element) {
            return;
        }
        
        // Hide current tooltip if different element
        if (currentTooltip && currentTooltip !== element) {
            hideTooltip(true); // immediate hide for different word
        }
        
        currentWord = word;
        currentTooltip = element;
        
        // Check if tooltip already exists
        let tooltip = document.querySelector('#tooltip-container');
        if (!tooltip) {
            // Create tooltip container (only one for the entire page)
            tooltip = document.createElement('div');
            tooltip.id = 'tooltip-container';
            tooltip.className = 'tooltip-content';
            document.body.appendChild(tooltip);
            
            // Prevent tooltip from closing when hovering over it
            tooltip.addEventListener('mouseenter', (e) => {
                e.stopPropagation();
                if (tooltipTimeout) {
                    clearTimeout(tooltipTimeout);
                    tooltipTimeout = null;
                }
            });
            
            tooltip.addEventListener('mouseleave', (e) => {
                e.stopPropagation();
                tooltipTimeout = setTimeout(() => hideTooltip(false), 300);
            });
            
            // Prevent clicks on tooltip from propagating
            tooltip.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }
        
        // Set loading state
        tooltip.innerHTML = '<div class="loading">Loading...</div>';
        tooltip.classList.add('active');
        
        // Position tooltip initially
        positionTooltip(tooltip, element);
        
        // Fetch data
        const data = await fetchTooltipData(word);
        
        if (data) {
            // Build tooltip content
            let html = `<div class="tooltip-description">${data.description}</div>`;
            html += '<div class="tooltip-links">';
            for (const link of data.links) {
                html += `<a href="${link.url}" target="_blank" class="tooltip-link">${link.text}</a>`;
            }
            html += '</div>';
            tooltip.innerHTML = html;
        } else {
            tooltip.innerHTML = '<div class="loading">No information available</div>';
        }
        
        // Reposition after content is loaded (size might have changed)
        positionTooltip(tooltip, element);
    }
    
    function hideTooltip(immediate = false) {
        const tooltip = document.querySelector('#tooltip-container');
        if (tooltip) {
            tooltip.classList.remove('active');
        }
        currentTooltip = null;
        currentWord = null;
    }
    
    function initTooltips() {
        // Prevent re-initialization causing infinite loops
        if (initialized) {
            return;
        }
        
        // Find all tooltip words and add event listeners
        document.querySelectorAll('.tooltip-word').forEach(element => {
            // Check if already initialized
            if (element.hasAttribute('data-tooltip-initialized')) {
                return;
            }
            element.setAttribute('data-tooltip-initialized', 'true');
            
            const word = element.dataset.word;
            
            element.addEventListener('mouseenter', (e) => {
                // Clear any pending hide
                if (tooltipTimeout) {
                    clearTimeout(tooltipTimeout);
                    tooltipTimeout = null;
                }
                // Add small delay before showing to prevent flicker
                if (showTimeout) {
                    clearTimeout(showTimeout);
                }
                showTimeout = setTimeout(() => {
                    showTooltip(element, word);
                }, 100);
            });
            
            element.addEventListener('mouseleave', (e) => {
                // Clear show timeout if leaving before tooltip shows
                if (showTimeout) {
                    clearTimeout(showTimeout);
                    showTimeout = null;
                }
                
                // Check if we're moving to the tooltip itself
                const relatedTarget = e.relatedTarget;
                if (relatedTarget && (relatedTarget.id === 'tooltip-container' || relatedTarget.closest('#tooltip-container'))) {
                    // Moving to tooltip, don't hide
                    return;
                }
                
                // Add delay before hiding to allow moving to tooltip
                tooltipTimeout = setTimeout(() => hideTooltip(false), 300);
            });
            
            // Handle mousemove to ensure tooltip stays visible
            element.addEventListener('mousemove', (e) => {
                if (currentWord === word && currentTooltip === element) {
                    // Already showing this tooltip, clear any hide timeout
                    if (tooltipTimeout) {
                        clearTimeout(tooltipTimeout);
                        tooltipTimeout = null;
                    }
                }
            });
        });
        
        initialized = true;
    }
    
    // Initialize tooltips when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTooltips);
    } else {
        // DOM is already loaded
        setTimeout(initTooltips, 100);
    }
    
    // Only watch for new content, not re-initialize everything
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1) { // Element node
                    // Check if it's a tooltip word or contains tooltip words
                    if (node.classList && node.classList.contains('tooltip-word')) {
                        if (!node.hasAttribute('data-tooltip-initialized')) {
                            initSingleTooltip(node);
                        }
                    } else if (node.querySelectorAll) {
                        node.querySelectorAll('.tooltip-word').forEach(el => {
                            if (!el.hasAttribute('data-tooltip-initialized')) {
                                initSingleTooltip(el);
                            }
                        });
                    }
                }
            });
        });
    });
    
    function initSingleTooltip(element) {
        if (element.hasAttribute('data-tooltip-initialized')) {
            return;
        }
        element.setAttribute('data-tooltip-initialized', 'true');
        
        const word = element.dataset.word;
        
        element.addEventListener('mouseenter', (e) => {
            if (tooltipTimeout) {
                clearTimeout(tooltipTimeout);
                tooltipTimeout = null;
            }
            if (showTimeout) {
                clearTimeout(showTimeout);
            }
            showTimeout = setTimeout(() => {
                showTooltip(element, word);
            }, 100);
        });
        
        element.addEventListener('mouseleave', (e) => {
            if (showTimeout) {
                clearTimeout(showTimeout);
                showTimeout = null;
            }
            
            const relatedTarget = e.relatedTarget;
            if (relatedTarget && (relatedTarget.id === 'tooltip-container' || relatedTarget.closest('#tooltip-container'))) {
                return;
            }
            
            tooltipTimeout = setTimeout(() => hideTooltip(false), 300);
        });
        
        element.addEventListener('mousemove', (e) => {
            if (currentWord === word && currentTooltip === element) {
                if (tooltipTimeout) {
                    clearTimeout(tooltipTimeout);
                    tooltipTimeout = null;
                }
            }
        });
    }
    
    // Start observing after initialization
    setTimeout(() => {
        observer.observe(document.body, { childList: true, subtree: true });
    }, 500);
    
    // Reposition tooltip on window resize/scroll
    window.addEventListener('resize', () => {
        if (currentTooltip) {
            const tooltip = document.querySelector('#tooltip-container');
            if (tooltip && tooltip.classList.contains('active')) {
                positionTooltip(tooltip, currentTooltip);
            }
        }
    });
    
    window.addEventListener('scroll', () => {
        if (currentTooltip) {
            const tooltip = document.querySelector('#tooltip-container');
            if (tooltip && tooltip.classList.contains('active')) {
                positionTooltip(tooltip, currentTooltip);
            }
        }
    });
</script>
'''