import os
import zipfile
from pathlib import Path

def main():
    scratch_dir = Path(__file__).parent
    os.makedirs(scratch_dir, exist_ok=True)
    
    # 1. Create spoofed image: a text file renamed to .jpg
    with open(scratch_dir / "spoofed.jpg", "w") as f:
        f.write("This is not a JPEG, it's just text!")
        
    # 2. Create PDF with JavaScript
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << >> /Contents 4 0 R >>\nendobj\n"
        b"4 0 obj\n<< /Length 50 >>\nstream\nhello world\n/JS (app.alert('Malware Triggered!'))\nendstream\nendobj\n"
        b"trailer\n<< /Size 4 /Root 1 0 R >>\n"
        b"%%EOF\n"
    )
    with open(scratch_dir / "test_js.pdf", "wb") as f:
        f.write(pdf_content)
        
    # 3. Create dummy PPTX (as a ZIP file containing XML files)
    pptx_path = scratch_dir / "test.pptx"
    with zipfile.ZipFile(pptx_path, 'w') as z:
        # docProps/core.xml
        core_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
            '  <dc:title>Test PowerPoint</dc:title>\n'
            '  <dc:creator>Jane Doe</dc:creator>\n'
            '  <cp:lastModifiedBy>John Smith</cp:lastModifiedBy>\n'
            '  <cp:revision>4</cp:revision>\n'
            '  <dcterms:created xsi:type="dcterms:W3CDTF">2026-06-25T10:00:00Z</dcterms:created>\n'
            '  <dcterms:modified xsi:type="dcterms:W3CDTF">2026-06-26T12:00:00Z</dcterms:modified>\n'
            '</cp:coreProperties>'
        )
        z.writestr('docProps/core.xml', core_xml)
        
        # docProps/app.xml
        app_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<ep:properties xmlns:ep="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">\n'
            '  <ep:Slides>15</ep:Slides>\n'
            '  <ep:Notes>2</ep:Notes>\n'
            '  <ep:PresentationFormat>On-screen Show (4:3)</ep:PresentationFormat>\n'
            '</ep:properties>'
        )
        z.writestr('docProps/app.xml', app_xml)
        # Empty placeholder
        z.writestr('[Content_Types].xml', '<Types></Types>')

    # 4. Create dummy PPTX with VBA macro (tampered pptx containing vbaProject.bin)
    pptx_macro_path = scratch_dir / "test_macro.pptx"
    with zipfile.ZipFile(pptx_macro_path, 'w') as z:
        z.writestr('docProps/core.xml', core_xml)
        z.writestr('docProps/app.xml', app_xml)
        z.writestr('[Content_Types].xml', '<Types></Types>')
        z.writestr('ppt/vbaProject.bin', b'COFFEE DUMMY VBA MACRO PROJECT BYTES')
        
    print("✓ Verification files generated successfully in scratch directory.")

if __name__ == "__main__":
    main()
