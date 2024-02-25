# import libraries
import numpy as np
from fpdf import  FPDF
from reportGenerator.pdfSectionsBuilder import *


def generate_pdf_for_current_3pl(current_3pl,period,all_3pls,date,
                                 df_reass_t1,reass_1_recommandations,df_reass_t2,reass_2_recommandations,df_reass_t3,reass_3_recommandations,
                                 df_nslu_t1,nslu_1_recommandations,df_nslu_t2,nslu_2_recommandations,df_nslu_t3,nslu_3_recommandations,
                                 df_cnm_t1,cnm_1_recommandations,df_cnm_t2,cnm_2_recommandations,df_cnm_t3,cnm_3_recommandations,
                                 gps_fraud_couriers,capus_couriers,check_in_no_work_couriers,
                                 total_funnel_ends,avg_total_funnel_moves,total_funnel_moves):

        hh = 0
        pdf = FPDF("P", "mm", "A4")
        pdf.add_page()
        pdf.set_font("Times", "B", 21)
        if period == "daily":
            report_title = all_3pls[current_3pl] + ": Rapport Quotidien"
        else:
            report_title = all_3pls[current_3pl] + ": Rapport Hebdomadaire"

        pdf.cell(0, 7, report_title, align="C")
        hh = adjust_height(pdf,hh, 9)
        hh += 9
        pdf.set_xy(10, hh)
        pdf.set_font("Times", "", 9)
        day_name = date.strftime("%A")
        if day_name.lower() == "monday":
            day_name = "Lundi"
        elif day_name.lower() == "tuesday":
            day_name = "Mardi"
        elif day_name.lower() == "wednesday":
            day_name = "Mercredi"
        elif day_name.lower() == "thursday":
            day_name = "Jeudi"
        elif day_name.lower() == "friday":
            day_name = "Vendredi"
        elif day_name.lower() == "saturday":
            day_name = "Samedi"
        else:
            day_name = "Dimanche"

        report_subtitle = ""
        if period == "daily":
            report_subtitle = day_name + ", " + str(date).split(" ")[0]
            pdf.cell(0, 25, report_subtitle, align="C", ln=2)
        hh += 26

        #### offenders
        pdf.set_xy(10, hh)
        pdf.set_font("Times", "B", 15)
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 7, "I. Les coursiers nécessitant une attention particulière: ", align="L")
        hh += 10
        pdf.set_xy(10, hh)

        if len(df_reass_t1) > 0:
            metric = "_reass_t1_"
            metric_title = "Coursiers avec une valeur métrique de réaffectation élevée (plus de 15%) :"
            metric_recommandations = reass_1_recommandations
            hh = add_metric_offenders_to_report(pdf,hh,period,current_3pl,df_reass_t1,metric,metric_title,metric_recommandations)
            
        if len(df_reass_t2) > 0:
            metric = "_reass_t2_"
            metric_title = "Coursiers avec une valeur métrique de réaffectation élevée (plus de 40%):"
            metric_recommandations = reass_2_recommandations
            hh = add_metric_offenders_to_report(pdf, hh, period, current_3pl, df_reass_t2, metric, metric_title,
                                                metric_recommandations)

        if len(df_reass_t3) > 0:
            metric = "_reass_t3_"
            metric_title = "Coursiers avec une valeur métrique de réaffectation élevée (plus de 60%):"
            metric_recommandations = reass_3_recommandations
            hh = add_metric_offenders_to_report(pdf, hh, period, current_3pl, df_reass_t3, metric, metric_title,
                                                metric_recommandations)

        if len(df_nslu_t1) > 0:
            metric = "_nslu_t1_"
            metric_title = "Coursiers avec une valeur métrique de non-présentation élevée (plus de 20%) :"
            metric_recommandations = nslu_1_recommandations
            hh = add_metric_offenders_to_report(pdf, hh, period, current_3pl, df_nslu_t1, metric, metric_title,
                                                metric_recommandations)

        if len(df_nslu_t2) > 0:
            metric = "_nslu_t2_"
            metric_title = "Coursiers avec une valeur métrique de non-présentation élevée (plus de 40%) :"
            metric_recommandations = nslu_2_recommandations
            hh = add_metric_offenders_to_report(pdf, hh, period, current_3pl, df_nslu_t2, metric, metric_title,
                                                metric_recommandations)
        if len(df_nslu_t3) > 0:
            metric = "_nslu_t3_"
            metric_title = "Coursiers avec une valeur métrique de non-présentation élevée (plus de 90%) :"
            metric_recommandations = nslu_3_recommandations
            hh = add_metric_offenders_to_report(pdf, hh, period, current_3pl, df_nslu_t3, metric, metric_title,
                                                metric_recommandations)

        if len(df_cnm_t1) > 0:
            metric = "_cnm_t1_"
            metric_title = "Coursiers avec une valeur métrique «immobile» élevée (plus de 20%) :"
            metric_recommandations = cnm_1_recommandations
            hh = add_metric_offenders_to_report(pdf, hh, period, current_3pl, df_cnm_t1, metric, metric_title,
                                                metric_recommandations)

        if len(df_cnm_t2) > 0:
            metric = "_cnm_t2_"
            metric_title = "Coursiers avec une valeur métrique «immobile» élevée (plus de 40%) :"
            metric_recommandations = cnm_2_recommandations
            hh = add_metric_offenders_to_report(pdf, hh, period, current_3pl, df_cnm_t2, metric, metric_title,
                                                metric_recommandations)
        if len(df_cnm_t3) > 0:
            metric = "_cnm_t3_"
            metric_title = "Coursiers avec une valeur métrique «immobile» élevée (plus de 80%) :"
            metric_recommandations = cnm_3_recommandations
            hh = add_metric_offenders_to_report(pdf, hh, period, current_3pl, df_cnm_t3, metric, metric_title,
                                                metric_recommandations)

        #### Fraud
        if period == "daily":
            hh = 20
            pdf.add_page()
            pdf.set_font("Times", "B", 15)
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 20, "II. Coursiers frauduleux:", align="L")
            hh += 5
            pdf.set_xy(10, hh)
            if len(gps_fraud_couriers) > 0:
                fraud = "_gps_fraud_"
                fraud_title = "Fraude GPS:"
                fraud_recommandations = ". Les coursiers de cette liste ont un score élevé de fraude GPS. Ils se sont déplacés sur une distance supérieure à 500 mètres avec une vitesse supérieure à 250 km/h. Veuillez vérifier et informer les coursiers mentionnés dans cette liste."
                hh = add_fraud_offenders_to_report(pdf,hh,period,current_3pl,gps_fraud_couriers,fraud_title,fraud,fraud_recommandations)

            if len(capus_couriers) > 0:
                fraud = "_capus_couriers_"
                fraud_title = "Fraude des Commandes Annulées:"
                fraud_recommandations = ". Les coursiers de cette liste ont un score élevé de fraude commandes annulées. Ils ont un nombre élevés de commandes annulées où ils n'ont pas respecté le processus de Glovo. Veuillez vérifier et informer les coursiers mentionnés dans cette liste."
                hh = add_fraud_offenders_to_report(pdf,hh,period,current_3pl,capus_couriers,fraud_title,fraud,fraud_recommandations)

            if len(check_in_no_work_couriers) > 0:
                check_in_no_work_couriers["excellence_score"] = check_in_no_work_couriers["excellence_score"].apply(lambda x: np.round(x, 2))
                fraud = "_check_in_no_work_"
                fraud_title = "Fraude \"sur le bord\":"
                fraud_recommandations = ". Ces coursiers font le \"check-in\" mais ils n'ont pas travaillé malgré que leurs score est elevé. Cela indique qu'ils sont restés en bordure de la carte pour éviter les expulsions et pour éviter également de travailler. Veuillez vérifier et informer les coursiers mentionnés dans cette liste."
                hh = add_fraud_offenders_to_report(pdf,hh,period,current_3pl,check_in_no_work_couriers,fraud_title,fraud,fraud_recommandations)

        #### stats
        pdf.add_page()
        pdf.set_font("Times", "B", 15)
        pdf.set_text_color(255, 0, 0)
        if period == "daily":
            n = "III"
        else:
            n = "II"
        pdf.cell(0, 20, n + ". Indicateurs 3PL VS Moyenne:", align="L")
        if (int(total_funnel_ends) > 0) or (int(total_funnel_moves) > 0):
            pdf.set_xy(10, 25)
            pdf.set_font("Times", "B", 13)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 7, str(int(total_funnel_ends)) + " avaient amélioré leurs performances V.S " + str(
                int(total_funnel_moves)) + " coursiers aux performances extrêmement faibles", align="C")
            pdf.set_xy(10, 33)
        pdf.image("content/reass.jpg", w=90, x=5, y=41)
        pdf.image("content/noshows.jpg", w=90, x=105, y=41)
        pdf.image("content/orders.jpg", w=90, x=5, y=141)
        if int(avg_total_funnel_moves) > 0:
            pdf.image("content/blocks.jpg", w=90, x=105, y=141)

        #### active couriers
        if period == "weekly":
            pdf.add_page()
            pdf.set_font("Times", "B", 15)
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 20, "III. Coursiers actives:", align="L")
            pdf.image("content/active.jpg", w=200, x=5, y=31)
        pdf.output("content/report_" + str(current_3pl) + ".pdf")

        return report_subtitle
