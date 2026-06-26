import sys
from pathlib import Path

# Ensure root package is in path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.extractors.registry import get_extractor

def run_tests():
    scratch_dir = Path(__file__).parent
    errors = []

    # 1. Test Extension Spoofing Detection
    try:
        spoofed_jpg = scratch_dir / "spoofed.jpg"
        extractor = get_extractor(str(spoofed_jpg))
        res = extractor._safe_extract()
        anom_str = "".join(res.get("anomalies", []))
        assert "Mismatched signature" in anom_str, f"Expected signature mismatch, got: {res}"
        print("✓ Test 1: Extension spoofing detected successfully.")
    except Exception as e:
        errors.append(f"Test 1 Failed: {e}")

    # 2. Test PDF JavaScript Detection
    try:
        pdf_js = scratch_dir / "test_js.pdf"
        extractor = get_extractor(str(pdf_js))
        res = extractor._safe_extract()
        anom_str = "".join(res.get("anomalies", []))
        assert "Embedded JavaScript detected" in anom_str, f"Expected JS anomaly, got: {res}"
        print("✓ Test 2: PDF JavaScript execution threat detected successfully.")
    except Exception as e:
        errors.append(f"Test 2 Failed: {e}")

    # 3. Test PPTX Parser & OOXML Property Extraction
    try:
        pptx = scratch_dir / "test.pptx"
        extractor = get_extractor(str(pptx))
        res = extractor._safe_extract()
        core = res.get("core_properties", {})
        pres = res.get("presentation_properties", {})
        assert core.get("author") == "Jane Doe", f"Expected Jane Doe, got {core.get('author')}"
        assert core.get("last_modified_by") == "John Smith", f"Expected John Smith, got {core.get('last_modified_by')}"
        assert pres.get("slide_count") == 15, f"Expected 15 slides, got {pres.get('slide_count')}"
        print("✓ Test 3: PPTX XML structure parsed and extracted successfully.")
    except Exception as e:
        errors.append(f"Test 3 Failed: {e}")

    # 4. Test Macro Detection
    try:
        pptx_macro = scratch_dir / "test_macro.pptx"
        extractor = get_extractor(str(pptx_macro))
        res = extractor._safe_extract()
        anom_str = "".join(res.get("anomalies", []))
        assert "Embedded VBA Macros" in anom_str, f"Expected macro warning, got: {res}"
        print("✓ Test 4: Office Macro threat detected successfully.")
    except Exception as e:
        errors.append(f"Test 4 Failed: {e}")

    # Summary
    if errors:
        print("\n✗ Some tests failed:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\n🎉 All automated metadata forensic tests passed successfully!")

if __name__ == "__main__":
    run_tests()
