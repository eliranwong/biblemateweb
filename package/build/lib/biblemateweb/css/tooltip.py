def get_tooltip_css(dark_mode):
    return f'''
<style>
    .tooltip-word {{
        cursor: help;
        position: relative;
        display: inline-block;
    }}
    
    .tooltip-content {{
        position: fixed; /* Changed from absolute to fixed for viewport-based positioning */
        background: {'#191919' if dark_mode else '#f7f5f5'};
        border: 1px solid #ccc;
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        min-width: 250px;
        max-width: 350px;
        max-height: 90%;          /* Limit height */
        overflow-y: auto;           /* Enable vertical scrolling */
        z-index: 10000;
        display: none;
        pointer-events: none; /* Prevent interference initially */
    }}
    
    .tooltip-content.active {{
        display: block;
        pointer-events: auto; /* Enable interaction when active */
    }}
    
    /* Position variants */
    .tooltip-content.position-top {{
        /* Arrow pointing down */
    }}
    
    .tooltip-content.position-bottom {{
        /* Arrow pointing up */
    }}
    
    .tooltip-content.position-left {{
        /* Arrow pointing right */
    }}
    
    .tooltip-content.position-right {{
        /* Arrow pointing left */
    }}
    
    /* Arrow styles for different positions */
    .tooltip-arrow {{
        position: absolute;
        width: 0;
        height: 0;
        border-style: solid;
    }}
    
    .tooltip-arrow.arrow-down {{
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        border-width: 10px 10px 0 10px;
        border-color: white transparent transparent transparent;
    }}
    
    .tooltip-arrow.arrow-up {{
        top: -10px;
        left: 50%;
        transform: translateX(-50%);
        border-width: 0 10px 10px 10px;
        border-color: transparent transparent white transparent;
    }}
    
    .tooltip-arrow.arrow-left {{
        left: -10px;
        top: 50%;
        transform: translateY(-50%);
        border-width: 10px 10px 10px 0;
        border-color: transparent white transparent transparent;
    }}
    
    .tooltip-arrow.arrow-right {{
        right: -10px;
        top: 50%;
        transform: translateY(-50%);
        border-width: 10px 0 10px 10px;
        border-color: transparent transparent transparent white;
    }}
    
    /* Arrow borders for different positions */
    .tooltip-arrow-border {{
        position: absolute;
        width: 0;
        height: 0;
        border-style: solid;
    }}
    
    .tooltip-arrow-border.arrow-down {{
        bottom: -11px;
        left: 50%;
        transform: translateX(-50%);
        border-width: 11px 11px 0 11px;
        border-color: #ccc transparent transparent transparent;
    }}
    
    .tooltip-arrow-border.arrow-up {{
        top: -11px;
        left: 50%;
        transform: translateX(-50%);
        border-width: 0 11px 11px 11px;
        border-color: transparent transparent #ccc transparent;
    }}
    
    .tooltip-arrow-border.arrow-left {{
        left: -11px;
        top: 50%;
        transform: translateY(-50%);
        border-width: 11px 11px 11px 0;
        border-color: transparent #ccc transparent transparent;
    }}
    
    .tooltip-arrow-border.arrow-right {{
        right: -11px;
        top: 50%;
        transform: translateY(-50%);
        border-width: 11px 0 11px 11px;
        border-color: transparent transparent transparent #ccc;
    }}
    
    .tooltip-description {{
        margin-bottom: 10px;
        color: {'white' if dark_mode else 'black'};
        font-size: 14px;
    }}
    
    .tooltip-links {{
        display: flex;
        flex-direction: column;
        gap: 5px;
    }}
    
    .tooltip-link {{
        color: #0066cc;
        text-decoration: none;
        font-size: 13px;
        padding: 4px 8px;
        border-radius: 4px;
        transition: background-color 0.2s;
    }}
    
    .tooltip-link:hover {{
        background-color: #f0f0f0;
    }}
    
    .loading {{
        color: #666;
        font-style: italic;
    }}
</style>
'''