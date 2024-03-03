import pandas as pd
import json
import requests
import time
import mysql.connector
from utilities.queries import query_kickouts_during_saturation


def load_data_from_livedb(query, attempts=3, delay=2):
    attempt = 1
    config = {
        "host": "maxscale-prod.internal.glovoapp.com",
        "user": "gs_weekly_pay",
        "password": "zuusija2eiYohngah1me",
        "database": "glovo_live",
    }
    while attempt < attempts + 1:
        try:
            cnx = mysql.connector.connect(**config)
        except:
            time.sleep(delay ** attempt)
            attempt += 1

    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            result = cursor.execute(query)
            rows = cursor.fetchall()
        cnx.close()
        return pd.DataFrame(rows)
    else:
        print("Could not connect")
        return None


def rebook_kickedout_couriers(token, courier_id=None, slot_id=None):
    if (courier_id is None) and (slot_id is None):
        df = pd.read_csv("data/TN kicked out couriers in current slot - Kickouts.csv")

        for index, row in df.iterrows():
            courier_id = row["courier_id"]
            slot_id = row["slot_id"]
            r = unbook_slot(token, courier_id, slot_id)
            print(courier_id,slot_id,r)
            r = book_slot(token, courier_id, slot_id)
            print(courier_id,slot_id,r)
    else:
        r = unbook_slot(token, courier_id, slot_id)
        print(courier_id,slot_id,r)
        r = book_slot(token, courier_id, slot_id)
        print(courier_id,slot_id,r)


def get_new_token(admin_credentials):
    url = "https://glovoapp.onelogin.com/oidc/2/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": admin_credentials['ONELOGIN_CLIENT_ID'],
        "client_secret": admin_credentials['ONELOGIN_CLIENT_SECRET'],
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    request_sso_token = requests.request(
        "POST",
        url,
        headers=headers,
        data=payload,
    ).json()

    sso_token = request_sso_token.get("access_token")

    if sso_token is None:
        raise Exception("Client_id and/or client_secret are wrongs.")

    url = "https://adminapi.glovoapp.com/oauth/operator_token"

    payload = {
        "grantType": "client_credentials",
        "ssoToken": sso_token,
        "link_token": "https://adminapi.glovoapp.com/oauth/operator_token",
    }
    headers = {"Content-Type": "application/json"}

    try:
        return requests.request(
            "POST",
            url,
            headers=headers,
            json=payload,
        ).json().get("accessToken")
    except Exception as e:
        raise Exception(
            "Something went wrong when trying to authenticate to AdminAPI"
            f"Exception is: {e}",
        )


def give_cash(token, courier_id, amount):
    amount = str(amount)
    link = "https://adminapi.glovoapp.com/admin/couriers/" + str(courier_id) + "/give_cash"
    try:
        r = requests.post(link, headers={'Content-Type': 'application/json', 'authorization': token}, json={
            "amount": amount}).json()
        print(r)
        try:
            return r['cashBalance']
        except Exception:
            return r


    except Exception:
        print('Something went wrong, impossible to give cash')

        return r
        

def unbook_slot(token, courier_id, slot_id):
    link = 'https://adminapi.glovoapp.com/admin/scheduling/couriers/' + str(courier_id) + '/slots/' + str(
        slot_id) + '/unbook'

    try:
        r = requests.post(link, headers={'Content-Type': 'application/json', 'authorization': token}, json={})

        if r.status_code == 200:
            return True, r.json()
        else:
            return False, r.text

    except Exception:
        return False, 'Error unbook_slot'

def book_slot(token, courier_id, slot_id):
    link = 'https://adminapi.glovoapp.com/admin/scheduling/couriers/' + str(courier_id) + '/slots/' + str(
        slot_id) + '/book'

    try:
        r = requests.post(link, headers={'Content-Type': 'application/json', 'authorization': token}, json={})

        if r.status_code == 200:
            return True, r.json()
        else:
            return False, r.text

    except Exception:
        return False, 'Error book_slot'


def collect_cash(token, courier_id, amount):
    amount = str(amount)
    link = "https://adminapi.glovoapp.com/admin/couriers/" + str(courier_id) + "/collect_cash"
    try:
        r = requests.post(link, headers={'Content-Type': 'application/json', 'authorization': token}, json={
            "amount": amount}).json()
        print(r)
        try:
            return r['cashBalance']
        except Exception:
            if 'Amount to be collected is bigger than the current balance' in r['error']['message']:
                return 'Amount to be collected is bigger than the current balance'
            else:
                return r


    except Exception:
        print('Something went wrong, impossible to give cash')

        return 'Error'


# Function that disables couriers and keep other settings the same
def courier_enable(token, courier_id):
    try:
        json_admin_data = {
            "status": "ENABLED",
            "statusReason": "OTHER_REENABLING"
        }
        # post updated info
        link = 'https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id) + '/secondary_settings'
        r = requests.put(link,
                         headers={'Content-Type': 'application/json',
                                  'authorization': token},
                         json=json_admin_data).json()
        return r
    except Exception:
        raise Exception('Something went wrong, impossible to give cash')


# Function that disables couriers and keep other settings the same
def courier_block(token, courier_id):
    try:
        json_admin_data = {
            "status": "BLOCKED",
            "statusReason": "OTHER"
        }
        # post updated info
        link = 'https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id) + '/secondary_settings'
        r = requests.put(link,
                         headers={'Content-Type': 'application/json',
                                  'authorization': token},
                         json=json_admin_data).json()
        return r
    except Exception:
        raise Exception('Something went wrong, impossible to give cash')



def courier_disable(token, courier_id):
    try:
        json_admin_data = {
            "status": "DISABLED",
            "statusReason": "VOLUNTARY_LEAVE"
        }
        # post updated info
        link = 'https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id) + '/secondary_settings'
        r = requests.put(link,
                         headers={'Content-Type': 'application/json',
                                  'authorization': token},
                         json=json_admin_data).json()
        return r
    except Exception:
        raise Exception('Cant disable courier')


def change_vehicle(token, courier_id, vehicle):
    try:
        # get courier settings variables to keep the same and only change "enabled"
        res = requests.get('https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id),
                           headers={'Content-Type': 'application/json', 'authorization': token})
        text = res.text
        data = json.loads(text)

        #json_admin_data = {
         #   "enabled": "fase",
         #   "staff": data['isStaff'],
         #   "hiddenContentAccess": data['hiddenContentAccess'],
         #   "materialReceived": data['materialReceived'],
         #   "box": data['hasBox'],
         #   "mcc": data['mcc'],
         #   "transport": data['transport']
        #}
        json_admin_data = {
            "box": "true",
            "businessModel": "FREE_MODEL",
            "hasElectricTransport": False,
            "materialReceived": True,
            "mcc": False,
            "transport": vehicle
        }

        # post updated info
        link = 'https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id) + '/primary_settings'
        r = requests.put(link,
                         headers={'Content-Type': 'application/json',
                                  'authorization': token},
                         json=json_admin_data).json()
        return r
    except Exception:
        raise Exception('Something went wrong, impossible to give cash')


def change_iban(token, courier_id, iban):
    try:
        # get courier settings variables to keep the same and only change "enabled"
        res = requests.get('https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id),
                           headers={'Content-Type': 'application/json', 'authorization': token})
        text = res.text
        data = json.loads(text)

        json_admin_data = {
            "iban": iban
        }

        # post updated info
        link = 'https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id)
        r = requests.put(link,
                         headers={'Content-Type': 'application/json',
                                  'authorization': token},
                         json=json_admin_data).json()
        return r
    except Exception:
        raise Exception('Something went wrong, impossible to change iban')


def update_store_address_id(token, store_address_id):
    link = 'https://adminapi.glovoapp.com/admin/storeaddresses/' + str(store_address_id)

    try:
        r = requests.get(link, headers={'Content-Type': 'application/json', 'authorization': token}, json={})
        if r.status_code == 200:
            json_store = r.json()
            aux_json_store = r.json()

            try:
                json_store['openingTimes']['7'] = aux_json_store['openingTimes']['1']
            except Exception:
                json_store['openingTimes']['7'] = []
            try:
                json_store['openingTimes']['1'] = aux_json_store['openingTimes']['2']
            except Exception:
                json_store['openingTimes']['1'] = []
            try:
                json_store['openingTimes']['2'] = aux_json_store['openingTimes']['3']
            except Exception:
                json_store['openingTimes']['2'] = []
            try:
                json_store['openingTimes']['3'] = aux_json_store['openingTimes']['4']
            except Exception:
                json_store['openingTimes']['3'] = []
            try:
                json_store['openingTimes']['4'] = aux_json_store['openingTimes']['5']
            except Exception:
                json_store['openingTimes']['4'] = []
            try:
                json_store['openingTimes']['5'] = aux_json_store['openingTimes']['6']
            except Exception:
                json_store['openingTimes']['5'] = []
            try:
                json_store['openingTimes']['6'] = aux_json_store['openingTimes']['7']
            except Exception:
                json_store['openingTimes']['6'] = []

            return True, json_store
        else:
            return False, r.text

    except Exception:
        return False, 'Error get_store_address_id_luis_checkin'


def update_time_store(token, store_address_id, json_update_store):
    link = 'https://adminapi.glovoapp.com/admin/storeaddresses/' + store_address_id
    get_data = requests.get(link, headers={'Content-Type': 'application/json', 'authorization': token}).json()

    get_data["openingTimes"] = json_update_store

    try:
        r = requests.put(link, headers={'Content-Type': 'application/json', 'authorization': token},
                         json=get_data)

        if r.status_code == 200:
            return True, r.text
        else:
            return False, r.text

    except Exception:
        return False, 'Error update_store_address_id'


def change_city(token, store_address_id):
    link = 'https://adminapi.glovoapp.com/admin/stores/' + store_address_id + '/details'
    get_data = requests.get(link, headers={'Content-Type': 'application/json', 'authorization': token}).json()

    print(get_data)
    get_data["cityCode"] = 'BES'
    print(get_data)
    get_data = '{ "id": 260992, "name": "Flower Shop", "slug": null, "motherStoreId": null, "categoryId": 1312, "imageId": "Stores/qnjthr73khxjyfmjhwu6", "itemsType": "CATEGORIZED", "enabled": true, "cityCode": "TIS", "forcedlyClosed": false, "emulateOpen": false, "position": 0, "dayServiceFee": null, "nightServiceFee": null, "filters": [ { "id": 34745, "name": "Flowers" } ], "dayPurchasesCommission": null, "nightPurchasesCommission": null, "cartUniqueElements": null, "cartTotalElements": null, "note": null, "disableReason": null, "salesSupervisor": null, "accountManager": null, "hidden": false, "menuDataurl": null, "boxRequired": false, "orderReviewRequired": false, "dayOverriddenBaseDeliveryFee": 6, "nightOverriddenBaseDeliveryFee": 6, "dayYieldPercentage": null, "nightYieldPercentage": null, "dayDeliveryFeeCap": null, "nightDeliveryFeeCap": null, "overriddenWallPosition": null, "maximumDeliveryDistance": 4000, "topSellersEnabled": true, "reorderEnabled": true, "suggestionKeywords": "", "customDescriptionAllowed": false, "productsInformationText": null, "productsInformationLink": null, "mcd": false, "superGlovo": false, "minimumBasket": { "tiers": [] }, "allowsLoyaltyCards": false, "maxCourierDistanceForNotifications": 1000, "food": false, "specialRequirementsAllowed": false, "basketLimitAmount": null, "basketLimitSize": null, "schedulingEnabled": true, "useGlovoCategorization": false, "topFifty": false, "bigChain": false, "preferred": false, "mergeAndAcquisition": false, "isManagerSectionEnabled": true, "allowBasketFees": false, "storeParentId": null, "storeSelfRefundPolicy": null, "cutleryRequestAllowed": false, "storeViewType": "LIST_VIEW", "badWeatherSurcharge": { "gen1FeeEnabled": false, "gen1FeeCents": 0, "gen1FeePartnerPercentage": 0 }, "returnBannerEnabled": false, "returnBannerText": null, "returnBannerLink": null, "canAccessManagerPortal": true, "creationTime": 1639069956000, "categoryInfo": { "id": 1312, "name": "PHARMACY_TN", "title": { "ar": "الجمال والصحة", "pt": "Cuidados Pessoais", "en": "Health&Beauty", "fr": "Hygiène et beauté", "es": "Cuidado personal" } }, "rating": null, "description": null, "tags": [], "menuDatasource": null, "deleted": false, "productCatalogId": 9267759, "storeDeepLink": "https://link.glovoapp.com/5NHP5bSTQlb", "isIntegrationOrDatasourcePartner": false, "motherStore": null, "disableMenuStoreAddressId": null, "selfRefundPolicy": null }'
    try:
        r = requests.patch('https://adminapi.glovoapp.com/admin/stores/' + store_address_id, headers={'Content-Type': 'application/json', 'authorization': token},
                         json=get_data)
        print(r)

        if r.status_code == 200:
            return True, r.text
        else:
            return False, r.text

    except Exception:
        return False, 'Error update_store_address_id'


def edit_description(token, courier_id, text):

    link_get = 'https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id)
    link = 'https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id) + "/profile"

    get_data = requests.get(link_get, headers={'Content-Type': 'application/json', 'authorization': token}).json()

    try:
        json_admin_data = {'phone': get_data["phoneNumber"], 'name': get_data["name"], 'firstSurname': get_data["firstSurname"],
                            'email': get_data["email"], "description": text}
        # post updated info
        r = requests.put(link,
                         headers={'Content-Type': 'application/json',
                                  'authorization': token},
                         json=json_admin_data).json()
        return r

    except Exception:
        print('Something went wrong, impossible to give cash')

        return 'Error'


def move_tags(token, courier_id_old, courier_id_new):
    #Get tags of old_courier_id
    tagIds_old = []
    tags_old_json = requests.get(
        f"https://adminapi.glovoapp.com/admin/entity_tagging/tagged_entities/COURIER/" + str(courier_id_old),
        headers={
            "Content-Type": "application/json",
            "authorization": token}).json()
    for value in range(len(tags_old_json["tags"])):
        tagId_old = tags_old_json["tags"][value]["id"]
        tagIds_old.append(tagId_old)

    #Update tags to new courier
    json_admin_data = {"tagIds": tagIds_old}
    link = f"https://adminapi.glovoapp.com/admin/entity_tagging/tagged_entities/COURIER/"+str(courier_id_new)
    response = requests.put(
        link,
        headers={
            "Content-Type": "application/json",
            "authorization": token,
        },
        json=json_admin_data,
    )
    return response


def get_cash(token, courier_id):
    link_get = 'https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id)
    get_data = requests.get(link_get, headers={'Content-Type': 'application/json', 'authorization': token}).json()
    return get_data["cashBalance"]


def get_description(token, courier_id):
    link_get = 'https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id)
    get_data = requests.get(link_get, headers={'Content-Type': 'application/json', 'authorization': token}).json()
    return get_data["description"]


def move_profile_info(token, courier_id_old, courier_id_new):
    link_get = 'https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id_old)
    get_data = requests.get(link_get, headers={'Content-Type': 'application/json', 'authorization': token}).json()
    old_data = {
        "birthDate": get_data["birthDate"],
        "description": get_data["description"],
        "email": "NEWTN_"+get_data["email"],
        "firstSurname": get_data["firstSurname"],
        "name": get_data["name"],
        "phone": get_data["phoneNumber"],
        "secondSurname": get_data["secondSurname"]
    }
    link = f"https://adminapi.glovoapp.com/admin/couriers/" + str(courier_id_new) + "/profile"
    response = requests.put(
        link,
        headers={
            "Content-Type": "application/json",
            "authorization": token,
        },
        json=old_data,
    )
    return response

def move_invocing_detials(token, courier_id_old, courier_id_new):

    link_get = 'https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id_old)
    get_data = requests.get(link_get, headers={'Content-Type': 'application/json', 'authorization': token}).json()
    old_data = {
        "address": get_data["address"],
        "c3plId": get_data["c3plId"],
        "contractType": get_data["contractType"],
        "documentsFolderLink": get_data["documentsFolderLink"],
        "iban": get_data["iban"],
        "irpf": get_data["irpf"],
        "nif": get_data["nif"],
        "postalCode": get_data["postalCode"],
        "province": get_data["province"],
        "vatNumber": get_data["vatNumber"],
    }
    link = f"https://adminapi.glovoapp.com/admin/couriers/"+str(courier_id_new)+"/invoicing"
    response = requests.put(link,
                     headers={'Content-Type': 'application/json',
                              'authorization': token},
                     json=old_data).json()
    return response

def delete_chall(token, chall_id):
    link = 'https://api.glovoapp.com/courier-challenges/admin/challenges/'+chall_id
    return_mssg = requests.delete(link, headers={'Content-Type': 'application/json', 'authorization': token})
    print(return_mssg)



