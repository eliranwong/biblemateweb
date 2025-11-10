BIBLE_JS = """
<script>
    // --- Core JavaScript Logic ---
    function scrollToVerse(verseId) {
        const element = document.getElementById(verseId);
        if (element) {
            // Use scrollIntoView to move the element into the viewport
            element.scrollIntoView({
                // 'smooth' makes the scrolling animated, 'auto' is instant
                behavior: 'smooth',
                // 'start' brings the element to the top of the scrollable area
                block: 'start'
            });
            // Optional: Highlight the verse temporarily
            element.classList.add('bg-yellow-200', 'ring-2', 'ring-yellow-500', 'shadow-lg');
            setTimeout(() => {
                element.classList.remove('bg-yellow-200', 'ring-2', 'ring-yellow-500', 'shadow-lg');
            }, 2000); // Remove highlight after 2 seconds
        } else {
            console.error(`Element with ID '${verseId}' not found.`);
        }
    }
</script>
"""