from reportGenerator.utils import adjust_height
from PIL import Image


def add_metric_offenders_to_report(pdf,hh,period,current_3pl,df,metric,metric_title,metric_recommandations):

    pdf.set_font("Times", "B", 13)
    pdf.set_text_color(0, 0, 0)
    hh = adjust_height(pdf,hh, 7)
    hh += 7
    pdf.cell(0, 7,metric_title , align="L")
    im = Image.open(r"content/" + period + metric + str(current_3pl) + ".jpg")
    width, height = im.size
    height = (height / len(df )) * (len(df ) + 0.75) * 0.264583
    im = im.save("content/" + period + metric + str(current_3pl) + ".png")
    hh = adjust_height(pdf,hh, height)
    pdf.image("content/" + period + metric + str(current_3pl) + ".png", w=90, x=50, y=hh + 4)
    pdf.set_font("Times", "", 13)
    hh = hh + height
    hh += 7
    pdf.set_xy(10, hh)
    pdf.set_font("Times", "", 11)
    pdf.set_text_color(140, 15, 20)
    hh = adjust_height(pdf,hh, 7)
    pdf.cell(0, 7, "- Les actions à entreprendre:", align="L")
    pdf.set_xy(10, hh)
    pdf.set_font("Times", "", 11)
    pdf.set_text_color(0, 0, 0)
    if ("«immobile» élevée (plus de 80%) :" in metric_title) or ( "non-présentation élevée (plus de 90%) :" in metric_title):
        a_number = 7 * 4 + 25
    else:
        a_number = 7 * 3 + 9
    hh = adjust_height(pdf,hh, a_number)
    pdf.multi_cell(0, 7, txt=("\n * ").join(metric_recommandations.split(" / ")))
    hh = hh + a_number
    pdf.set_xy(10, hh)
    
    return hh


def add_fraud_offenders_to_report(pdf,hh,period,current_3pl,df,fraud_title,fraud,fraud_recommandations):
    
    pdf.set_font("Times", "B", 13)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, fraud_title, align="L")
    pdf.set_xy(10, hh)
    pdf.set_font("Times", "", 11)
    pdf.set_text_color(0, 0, 0)
    hh = adjust_height(pdf, hh, 7)
    pdf.multi_cell(0, 7, ("\n").join(fraud_recommandations.split(". ")), align="L")
    hh += 7 * 4
    im = Image.open(r"content/" + period + fraud + str(current_3pl) + ".jpg")
    width, height = im.size
    height = (height / len(df)) * (len(df)) * 0.264583
    hh = adjust_height(pdf, hh, height)
    im = im.save("content/" + period + fraud + str(current_3pl) + ".png")
    pdf.image("content/" + period + fraud + str(current_3pl) + ".png", w=90, x=50, y=hh + 4)
    hh = hh + height
    pdf.set_xy(10, hh)

    return hh
