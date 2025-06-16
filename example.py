from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=12)
text = "Hello, this is a test.\nDay 1: Wake up\nDay 2: Achieve greatness"
pdf.multi_cell(0, 10, text, align='L')
pdf.output("test_output.pdf")
