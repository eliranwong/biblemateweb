def get_original_js(dark_mode):
    return f"""
<script>
    // MOCK W3.JS (Polyfill to avoid external dependency)
    var w3 = {{
        addStyle: function(selector, prop, value) {{
            document.querySelectorAll(selector).forEach(function(el) {{
                 el.style.setProperty(prop, value);
            }});
        }}
    }};

    // Variable used in original script for host interoperability

    function hl0(id, cl, sn) {{
        if (cl != '') {{
            w3.addStyle('.c'+cl,'background-color','');
        }}
        if (sn != '') {{
            w3.addStyle('.G'+sn,'background-color','');
        }}
        if (id != '') {{
            var focalElement = document.getElementById('w'+id);
            if (focalElement != null) {{
                focalElement.style.background='';
            }}
        }}
    }}

    function hl1(id, cl, sn) {{
        if (cl != '') {{
            w3.addStyle('.c'+cl,'background-color','{"#d48f28" if dark_mode else "PAPAYAWHIP"}');
        }}
        if (sn != '') {{
            w3.addStyle('.G'+sn,'background-color','{"#5d85fc" if dark_mode else "#E7EDFF"}');
        }}
        if (id != '') {{
            var focalElement = document.getElementById('w'+id);
            if (focalElement != null) {{
                focalElement.style.background='{"#5a64b0" if dark_mode else "#C9CFFF"}';
            }}
        }}
    }}
</script>
"""