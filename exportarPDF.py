from fpdf import FPDF

def exportarProductos(cadena,lista):
    pdf = FPDF(orientation = 'P', unit = 'mm', format = 'A4')
    pdf.add_page()

    print(lista)
    pdf.set_font("Arial","",15)

    #Titulo
    pdf.cell(w=0, h=15, txt="Reporte", border=1, ln=1, align="C", fill=0)

    #Encabezado
    pdf.cell(w=20,h=15, txt="ID", border=1, align="C", fill=0)
    pdf.cell(w=50,h=15, txt="Nombre", border=1, align="C", fill=0)
    pdf.cell(w=40,h=15, txt="Costo", border=1, align="C", fill=0)
    pdf.cell(w=40,h=15, txt="Stock", border=1, align="C", fill=0)
    pdf.multi_cell(w=40,h=15, txt="Ventas", border=1, align="C", fill=0)

    for valor in lista:
        pdf.cell(w=20,h=15, txt=str(valor[0]), border=1, align="C", fill=0)
        pdf.cell(w=50,h=15, txt=valor[1], border=1, align="C", fill=0)
        pdf.cell(w=40,h=15, txt=f"$ {str(valor[2])}", border=1, align="C", fill=0)
        pdf.cell(w=40,h=15, txt=str(valor[3]), border=1, align="C", fill=0)
        pdf.multi_cell(w=40,h=15, txt=str(valor[4]), border=1, align="C", fill=0)


    pdf.output(f"{cadena}.pdf")