def write_email_for_current_3pl(period,current_3pl,all_3pls,funnels_3pls,messages,report_subtitle):

    if period == "daily":
        subject = all_3pls[current_3pl] + " - Bilan quotidien des performances: " + report_subtitle
        intro = "<span style='font-family:tahoma;'>Bonjour " + all_3pls[current_3pl] + ",<br><br>J'espère que cet e-mail vous trouvera bien.<br><br>Vous trouverez ci-dessous nos indicateurs de performance clés (KPI) d'hier, ainsi qu'une proposition de plan d'action pour les coursiers répertoriés dans la liste ci-dessous.</span>"
        if len(funnels_3pls[current_3pl]) > 0:
            first = ""
            second = ""
            last = ""

            for courier in funnels_3pls[current_3pl]:
                if "accéléré" in courier:
                    last += "<li style='margin-bottom:5px;font-family:tahoma;'>" + courier + "</li>"
                elif "Félicitations" in courier:
                    first += "<li style='margin-bottom:5px;font-family:tahoma;'>" + courier + "</li>"
                else:
                    second += "<li style='margin-bottom:5px;font-family:tahoma;'>" + courier + "</li>"

            body = intro + "<br><br><b style='margin-bottom:5px;font-family:tahoma;'>Actions de AFM hier & Recommandations:</b><ul>" + first + "<br>" + second + "<br>" + last + "</ul>"
            body += "<span style='font-family:tahoma;'>  Nous comptons sur votre collaboration et vos compétences managériales pour ramener les performances des coursiers à suivre.<br><br>Cordialement,<br><br>Glovo Ops Team</span>"
            body += "<br><span style='font-family:tahoma;font-size:11px;color:red'>Veuillez <b>ne pas répondre</b> au rapport quotidien</span>"
        else:
            body = intro
            body += "<span style='font-family:tahoma;'>  Nous comptons sur votre collaboration et vos compétences managériales pour ramener les performances des coursiers à suivre.<br><br>Cordialement,<br><br>Glovo Ops Team</span>"
            body += "<br><span style='font-family:tahoma;font-size:11px;color:red'>Veuillez <b>ne pas répondre</b> au rapport quotidien</span>"

    else:
        subject = all_3pls[current_3pl] + " - Bilan hebdomadaire des performances: "
        intro = "<span style='font-family:tahoma;'>Bonjour " + all_3pls[current_3pl] + ",<br><br>J'espère que cet e-mail vous trouvera bien.<br><br>Vous trouverez ci-dessous nos indicateurs de performance clés (KPI) de la semaine derniére. Merci de partager avec nous les actions prises cette semaine à propos les coursiers répertoriés dans le rapport ci-dessous ainsi que pour améliorer votre flotte.</span>"
        body = intro + "<span style='font-family:tahoma;'>  Nous comptons sur votre collaboration et vos compétences managériales pour ramener les performances des coursiers à suivre.<br><br>Cordialement,<br><br>Glovo Ops Team</span>"
        body += "<br><span style='font-family:tahoma;font-size:11px;color:blue'>(Merci de <b>répondre</b> par un email contenant les actions pris par vous la semaine derniére)</span>"

    messages[current_3pl] = {"subject": subject, "body": body,
                             "file": "content/report_" + str(current_3pl) + ".pdf"}

    return messages