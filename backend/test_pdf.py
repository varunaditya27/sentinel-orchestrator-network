from fpdf import FPDF

try:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Test PDF", ln=1, align="C")
    
    # Output as string and encode
    pdf_string = pdf.output(dest='S')
    print(f"Type of output: {type(pdf_string)}")
    
    pdf_bytes = pdf_string.encode('latin-1')
    print(f"Type of bytes: {type(pdf_bytes)}")
    print(f"Length of bytes: {len(pdf_bytes)}")
    
    with open("test_output.pdf", "wb") as f:
        f.write(pdf_bytes)
        
    print("PDF written successfully.")
    
except Exception as e:
    print(f"Error: {e}")
