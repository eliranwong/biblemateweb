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

    function getWordSelector(id) {{
        var selector = '[id="w' + id + '"]';
        if (/^[0-9]+$/.test(id)) {{
            var padded = id.padStart(6, '0');
            var unpadded = String(parseInt(id, 10));
            if (padded !== unpadded) {{
                selector = '[id="w' + padded + '"], [id="w' + unpadded + '"]';
            }}
        }}
        return selector;
    }}

    function hl0(id, cl, sn) {{
        if (cl != '') {{
            w3.addStyle('.c'+cl,'background-color','');
        }}
        if (sn != '') {{
            w3.addStyle('.G'+sn,'background-color','');
        }}
        if (id != '') {{
            document.querySelectorAll(getWordSelector(id)).forEach(function(el) {{
                el.style.background = '';
            }});
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
            document.querySelectorAll(getWordSelector(id)).forEach(function(el) {{
                el.style.background = '{"#5a64b0" if dark_mode else "#C9CFFF"}';
            }});
        }}
    }}

    function getHighlightArgs(el) {{
        var id = '';
        if (el.id && el.id.charAt(0) === 'w') {{
            id = el.id.slice(1);
        }}
        var cl = '';
        var sn = '';
        el.classList.forEach(function(c) {{
            if (!cl && /^ch?\\d+$/.test(c)) {{
                cl = c.slice(1);
            }} else if (!sn && /^GE?\\d+$/.test(c)) {{
                sn = c.slice(1);
            }}
        }});
        return [id, cl, sn];
    }}

    document.addEventListener('mouseover', function(e) {{
        var el = e.target.closest('heb[id], grk[id], eng[class]');
        if (!el || el.hasAttribute('onmouseover')) return;
        if (e.relatedTarget && el.contains(e.relatedTarget)) return;
        var args = getHighlightArgs(el);
        hl1(args[0], args[1], args[2]);
    }});

    document.addEventListener('mouseout', function(e) {{
        var el = e.target.closest('heb[id], grk[id], eng[class]');
        if (!el || el.hasAttribute('onmouseout')) return;
        if (e.relatedTarget && el.contains(e.relatedTarget)) return;
        var args = getHighlightArgs(el);
        hl0(args[0], args[1], args[2]);
    }});
</script>
"""