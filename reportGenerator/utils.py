# import libraries
import pandas as pd


def style_checkin_fraud_df_in_report(dff):
    df = dff.copy()
    # Create a dictionary to hold the style properties
    whole_style_dict = {
        'background-color': '#ffffff',
        'border': '1px solid black',
        'height': "50px!important",
        'font-family': 'Comfortaa',
        'text-align': 'left'
    }

    df["courier_id"] = df["courier_id"].apply(lambda x: str(int(x)))
    df = df.rename(columns={'courier_id': "ID",
                            'first_name': "Prénom",
                            'last_name': "Nom",
                            "adress": "Adresse",
                            "excellence_score": "Score",
                            "n_slots_booked": "Heures Reservés",
                            "n_slots_checked_in": "Heures Travaillés",
                            "num_assignments": "Commandes Assignés"}).copy()
    df = df.set_index('ID').copy()
    df.index.name = None
    styled_df = df.style.set_properties(subset=pd.IndexSlice[:, :], **whole_style_dict)

    # Style the row background color
    styled_df = styled_df.set_table_styles([
        {'selector': 'tr', 'props': [('background-color', 'white'),
                                     ('border', '1x solid black'),
                                     ('font-family', 'sans-serif')]},
        {'selector': 'th', 'props': [('background-color', 'white'),
                                     ('border', '1px solid black'),
                                     ("text-align", "center"),
                                     ("text-transform", "capitalize"),
                                     ('background-color', '#e1e1e1')]}
    ])

    # Return the styled dataframe
    return styled_df

def style_df(df):
    # Create a dictionary to hold the style properties
    whole_style_dict = {
        'background-color': '#ffffff',
        'border': '1px solid black',
        'height': "50px!important",
        'font-family': 'Comfortaa',
        'text-align': 'left'
    }
    out_style = {
        'background-color': '#ffffff',
        'font-weight': 'bold',
        'color': 'green',
        'text-align': 'left'
    }
    accel_style = {
        'background-color': '#ffffff',
        'font-weight': 'bold',
        'color': 'red',
        'text-align': 'left'
    }
    blocked_style = {
        'background-color': '#f08181',
        'font-weight': 'bold',
        'color': 'white',
        'text-align': 'left'
    }

    styled_df = df.style.set_properties(subset=pd.IndexSlice[:, :], **whole_style_dict)
    dangers = df[df["Accelerated"] == "True"].index
    styled_df = styled_df.set_properties(subset=pd.IndexSlice[dangers, :], **accel_style)
    outs = df[df["Step"] == "END"].index
    styled_df = styled_df.set_properties(subset=pd.IndexSlice[outs, :], **out_style)
    blockeds = df[df["Step"] == "4"].index
    styled_df = styled_df.set_properties(subset=pd.IndexSlice[blockeds, :], **blocked_style)

    # Style the row background color
    styled_df = styled_df.set_table_styles([
        {'selector': 'tr', 'props': [('background-color', 'white'),
                                     ('border', '1x solid black'),
                                     ('font-family', 'Arial, Helvetica, sans-serif')]},
        {'selector': 'th', 'props': [('background-color', 'white'),
                                     ('border', '1px solid black'),
                                     ("text-align", "center"),
                                     ("text-transform", "capitalize"),
                                     ('background-color', '#e1e1e1')]}
    ])

    # Return the styled dataframe
    return styled_df

def style_df_in_report(dff):
        df = dff.copy()
        # Create a dictionary to hold the style properties
        whole_style_dict = {
            'background-color': '#ffffff',
            'border': '1px solid black',
            'height': "50px!important",
            'font-family': 'Comfortaa',
            'text-align': 'left'
        }
        blocked_style = {
            'background-color': '#f08181',
            'font-weight': 'bold',
            'color': 'white',
            'text-align': 'left'
        }

        df["courier_id"] = df["courier_id"].apply(lambda x: str(int(x)))
        df = df.rename(columns={'courier_id': "ID", 'first_name': "Prénom", 'last_name': "Nom", "phone": "Téléphone",
                                'is_worst_5_percent': "Pire 5 %?"}).copy()
        df = df[["ID", "Prénom", "Nom", "Pire 5 %?"]]
        df = df.set_index('ID').copy()
        df["Pire 5 %?"] = df["Pire 5 %?"].apply(lambda x: "Vrai" if x else "Faux")
        df.index.name = None
        styled_df = df.style.set_properties(subset=pd.IndexSlice[:, :], **whole_style_dict)
        blockeds = df[df["Pire 5 %?"] == "Vrai"].index
        styled_df = styled_df.set_properties(subset=pd.IndexSlice[blockeds, :], **blocked_style)

        # Style the row background color
        styled_df = styled_df.set_table_styles([
            {'selector': 'tr', 'props': [('background-color', 'white'),
                                         ('border', '1x solid black'),
                                         ('font-family', 'sans-serif')]},
            {'selector': 'th', 'props': [('background-color', 'white'),
                                         ('border', '1px solid black'),
                                         ("text-align", "center"),
                                         ("text-transform", "capitalize"),
                                         ('background-color', '#e1e1e1')]}
        ])

        # Return the styled dataframe
        return styled_df


def style_fraud_df_in_report(dff):
    df = dff.copy()
    # Create a dictionary to hold the style properties
    whole_style_dict = {
        'background-color': '#ffffff',
        'border': '1px solid black',
        'height': "50px!important",
        'font-family': 'Comfortaa',
        'text-align': 'left'
    }

    df["courier_id"] = df["courier_id"].apply(lambda x: str(int(x)))
    df = df.rename(columns={'courier_id': "ID",
                            'first_name': "Prénom",
                            'last_name': "Nom",
                            "adress": "Adresse"}).copy()
    df = df.set_index('ID').copy()
    df.index.name = None
    styled_df = df.style.set_properties(subset=pd.IndexSlice[:, :], **whole_style_dict)

    # Style the row background color
    styled_df = styled_df.set_table_styles([
        {'selector': 'tr', 'props': [('background-color', 'white'),
                                     ('border', '1x solid black'),
                                     ('font-family', 'sans-serif')]},
        {'selector': 'th', 'props': [('background-color', 'white'),
                                     ('border', '1px solid black'),
                                     ("text-align", "center"),
                                     ("text-transform", "capitalize"),
                                     ('background-color', '#e1e1e1')]}
    ])

    # Return the styled dataframe
    return styled_df

def adjust_height(pdf,hh,i):
    if hh +i > pdf.page_break_trigger :
        pdf.add_page()
        hh = 20
    return hh

def get_3pl_id(iban,df):
    try:
        return df.loc[df["IBAN"]==iban ,"ID"].values[0]
    except:
        return "101"