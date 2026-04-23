import os
import io
from flask import render_template

def create_brochure_from_html(output_filename, html_content):
    """
    Generates a PDF from the given HTML content string.
    
    Args:
        output_filename (str): Path to save the PDF.
        html_content (str): The full HTML string to render.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    # Helper to resolve paths
    def link_callback(uri, rel):
        """
        Convert HTML URIs to absolute system paths so xhtml2pdf can verify links and images.
        """
        # Define base paths
        # Assuming app.py is in the root of Documents/CavalierOne
        BASE_DIR = r"c:/Users/jason.m.chgv/Documents/CavalierOne"
        
        # Handle static/ resources
        if uri.startswith('/static/'):
            path = os.path.join(BASE_DIR, uri.lstrip('/'))
        elif uri.startswith('/resources/'):
            path = os.path.join(BASE_DIR, uri.lstrip('/'))
        elif uri.startswith('static/'):
             path = os.path.join(BASE_DIR, 'static', uri[7:])
        else:
            return uri # Return as is (maybe absolute already or http)

        # Make sure path exists
        if not os.path.isfile(path):
            print(f"PDF Gen Warning: Missing file {path}")
            return uri
            
        return path

    try:
        from xhtml2pdf import pisa
    except ImportError as e:
        print(f"[pdf_generator] xhtml2pdf not available: {e}")
        return False

    with open(output_filename, "wb") as result_file:
        pisa_status = pisa.CreatePDF(
            io.StringIO(html_content),
            dest=result_file,
            link_callback=link_callback
        )
    
    if pisa_status.err:
        print(f"Error generating PDF: {pisa_status.err}")
        return False
        
    print(f"PDF successfully generated: {output_filename}")
    return True

# Legacy function wrapper for compatibility if needed, 
# but mostly replaced by the new flow in app.py
def create_brochure(output_filename, data):
    """
    DEPRECATED: Use create_brochure_from_html in app.py logic instead.
    This is kept only if legacy calls depend on it fundamentally.
    """
    pass # Replaced by app.py handling the template rendering
