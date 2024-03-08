import pandas as pd
import requests
import datetime


class Admin:

    def __init__(self, token, refresh_token):
        self.token = token
        self.refresh_token = refresh_token

    def rebook_kickedout_couriers(self, file=None, courier_id=None, slot_id=None):
        message = "فرصة أخرى بش تعمل check-in !! :warning: فما برشة خدمة  :motor_scooter: فرصة بش دخل أكثر فلوس !!  :money_with_wings:"
        couriers_ids = []
        if (courier_id is None) and (slot_id is None):
            df = pd.read_csv(file)
            for index, row in df.iterrows():
                courier_id = row["courier_id"]
                couriers_ids.append(courier_id)
                slot_id = row["slot_id"]
                self.unbook_slot(courier_id, slot_id)
                r = self.book_slot(courier_id, slot_id)
                print(r)
            self.send_push_notification(couriers_ids,message)

        else:
            couriers_ids = [courier_id]
            self.unbook_slot(courier_id, slot_id)
            self.book_slot(courier_id, slot_id)
            self.send_push_notification(couriers_ids, message)

    def send_push_notification(self,couriers_ids,message):
        link = f"https://adminapi.glovoapp.com/admin/notifications/couriers"
        data = {
            "usersIds": couriers_ids,
            "body": message,
        }
        try:
            response = requests.post(link, headers={'Content-Type': 'application/json', 'authorization': self.token}, json=data).json()
            return True,response
        except:
            return False

    def setup_new_couriers_profiles(self, file):
        new_couriers = pd.read_csv(file)
        for index, courier_data in new_couriers.iterrows():
            try:
                date_formation = str(pd.to_datetime(courier_data["DATE DE FORMATION"])).split(" ")[0]
            except:
                date_formation = ""
            today = str(pd.to_datetime(datetime.datetime.now())).split(" ")[0]
            if (courier_data["Activé"]) and (date_formation == today):
                email = str(courier_data["EMAIL"]).strip()
                print(email)
                try:
                    courier_id = int(self.search("courier", email))
                except:
                    link = "https://adminapi.glovoapp.com/admin/couriers/search"
                    data = {
                        "cities": ["BES", "BIZ", "GBS", "HMN", "HMS", "NBL", "NSO", "SFX", "SOU", "TIE", "TIS"],
                        "query": str(int(courier_data["NUM DE TELEPHONE"]))
                    }
                    r = requests.post(link,
                                      headers={'Content-Type': 'application/json',
                                               'authorization': self.token},
                                      json=data).json()
                    courier_to_get = len(r["courierPhoneResults"]) - 1
                    courier_id = r["courierPhoneResults"][courier_to_get]["id"]
                print(courier_id)
                if courier_data["SAC"] == "GLOVO NEW":
                    bag_tag = 1417
                else:
                    bag_tag = 2154
                threepl_tag = courier_data["threepl_tag_id"]
                threepl_id = int(courier_data["threepl_id"].replace(",",""))
                threepl_iban = courier_data["threepl_iban"]
                vat_number = courier_data["vat_number"]
                cbz = courier_data["VILLE"]
                shift = courier_data["shift"]
                if shift == "normal (11-15 & 18-22)":
                    hours = [11,12,13,14,15,18,19,20,21,22]
                elif shift == "night (16-01)":
                    hours = [16,17,18,19,20,21,22,23,00,1]
                elif shift == "morning (9-14 & 18-21)":
                    hours = [9,10,11,12,13,14,18,19,20,21]
                elif shift == "part_time (18-23)":
                    hours = [18,19,20,21,22,23]

                self.add_tags(courier_id, [bag_tag,threepl_tag])
                self.add_invoicing_details(courier_id, threepl_id, threepl_iban, vat_number)
                self.book_slots_for_courier(courier_id, cbz, hours)

    def book_slots_for_courier(self, courier_id, cbz, hours):
        link_get = "https://adminapi.glovoapp.com/admin/scheduling/couriers/"+str(courier_id)+"/slots"
        get_data = requests.get(link_get, headers={'Content-Type': 'application/json', 'authorization': self.token}).json()
        slots_available = pd.DataFrame(get_data)
        slots_available = slots_available[slots_available["zoneAcronym"]==cbz]
        slots_available["startTime"] = slots_available["startTime"].astype(str)
        slots_available["startTime"] = slots_available["startTime"].apply(lambda x: int(x.split(" ")[1].split(":")[0]))
        slots_available["startTime"] = slots_available["startTime"].apply(lambda x: x in hours)
        slots_available = slots_available[slots_available["startTime"]]
        for slot_id in slots_available["id"]:
            r = self.book_slot(courier_id, slot_id)
        print("courier_id: ", courier_id, "successful booking: ", r)

    def add_invoicing_details(self, courier_id, threepl_id, threepl_iban, vat_number):
        vat_number = str(vat_number).strip()
        if len(vat_number) != 9:
            vat_number = " "
        link_get = 'https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id)
        get_data = requests.get(link_get, headers={'Content-Type': 'application/json', 'authorization': self.token}).json()
        data = {
            "address": get_data["address"],
            "c3plId": threepl_id,
            "contractType": get_data["contractType"],
            "documentsFolderLink": get_data["documentsFolderLink"],
            "iban": threepl_iban,
            "irpf": get_data["irpf"],
            "nif": get_data["nif"],
            "postalCode": get_data["postalCode"],
            "province": get_data["province"],
            "vatNumber": vat_number,
        }
        link = f"https://adminapi.glovoapp.com/admin/couriers/"+str(courier_id)+"/invoicing"
        response = requests.put(link, headers={'Content-Type': 'application/json', 'authorization': self.token}, json=data).json()
        return response

    def add_tags(self, courier_id, new_tags):
        # Get tags of old_courier_id
        tagIds_old = []
        tags_old_json = requests.get(f"https://adminapi.glovoapp.com/admin/entity_tagging/tagged_entities/COURIER/" + str(courier_id), headers={"Content-Type": "application/json", "authorization": self.token}).json()
        for value in range(len(tags_old_json["tags"])):
            tagId_old = tags_old_json["tags"][value]["id"]
            tagIds_old.append(tagId_old)

        for tag in new_tags:
            tagIds_old.append(tag)

        tagIds_old = list(set(tagIds_old))
        # Update tags to new courier
        json_admin_data = {"tagIds": tagIds_old}
        link = f"https://adminapi.glovoapp.com/admin/entity_tagging/tagged_entities/COURIER/" + str(courier_id)
        response = requests.put(link, headers={"Content-Type": "application/json", "authorization": self.token }, json=json_admin_data)
        return response

    def unbook_slot(self, courier_id, slot_id):
        link = 'https://adminapi.glovoapp.com/admin/scheduling/couriers/' + str(courier_id) + '/slots/' + str(slot_id) + '/unbook'
        try:
            r = requests.post(link, headers={'Content-Type': 'application/json', 'authorization': self.token}, json={})
            if r.status_code == 200:
                return True
            else:
                return False, r.text
        except Exception:
            return False, 'Error unbook_slot'

    def book_slot(self, courier_id, slot_id):
        link = 'https://adminapi.glovoapp.com/admin/scheduling/couriers/' + str(courier_id) + '/slots/' + str(slot_id) + '/book'
        try:
            r = requests.post(link, headers={'Content-Type': 'application/json', 'authorization': self.token}, json={})
            if r.status_code == 200:
                return True
            else:
                return False, r.text
        except Exception:
            return False, 'Error book_slot'

    def get_courier_kickouts(self, courier_id):
        link = "https://adminapi.glovoapp.com/admin/couriers/"+ str(courier_id) +"/kickouts?limit=500&page=0"
        r = requests.get(link,
                         headers={'Content-Type': 'application/json',
                                  'authorization': self.token}).json()
        kickouts = r["content"]
        kickouts_df = pd.DataFrame(kickouts)
        return kickouts_df

    def get_courier_performance(self, courier_id):

        return

    def get_order_details(self, order_id):
        link = "https://adminapi.glovoapp.com/admin/orders/"+str(order_id)+"/info"
        r = requests.get(link, headers={'Content-Type': 'application/json', 'authorization': self.token},).json()
        return r

    def search(self, field, query):
        link = "https://adminapi.glovoapp.com/admin/"+str(field)+"s/search"
        data = {
            "cities": ["BES", "BIZ", "GBS", "HMN", "HMS", "NBL", "NSO", "SFX", "SOU", "TIE", "TIS"],
            "query": query
        }
        r = requests.post(link,
                         headers={'Content-Type': 'application/json',
                                  'authorization': self.token},
                          json=data).json()
        print(r)
        if field == "order":
            id_result = r["orderCodeResults"]
        elif field == "courier":
            if r["courierEmailResults"] is not None:
                courier_to_get = len(r["courierEmailResults"]) - 1
                id_result = r["courierEmailResults"][courier_to_get]["id"]
            elif r["courierIdResults"] is not None:
                courier_to_get = len(r["courierIdResults"]) - 1
                id_result = r["courierIdResults"][courier_to_get]["id"]
            elif r["courierNameResults"] is not None:
                courier_to_get = len(r["courierNameResults"]) - 1
                id_result = r["courierNameResults"][courier_to_get]["id"]
            elif r["courierPhoneResults"] is not None:
                courier_to_get = len(r["courierPhoneResults"]) - 1
                id_result = r["courierPhoneResults"][courier_to_get]["id"]

        return id_result

    # reasons needs to be predefined like those in admin panel
    def courier_enable(self, courier_id, reason):
        try:
            json_admin_data = {
                "status": "ENABLED",
                "statusReason": reason
            }
            # post updated info
            link = 'https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id) + '/secondary_settings'
            r = requests.put(link,
                             headers={'Content-Type': 'application/json',
                                      'authorization': self.token},
                             json=json_admin_data).json()
            return r
        except Exception:
            raise Exception('Something went wrong, impossible enable courier')

    def courier_block(self, courier_id, reason, duration=None):
        try:
            json_admin_data = {
                "status": "BLOCKED",
                "statusReason": reason
            }
            if duration is not None:
                json_admin_data = {
                    "status": "BLOCKED",
                    "statusReason": reason,
                    "duration": duration
                }
            # post updated info
            link = 'https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id) + '/secondary_settings'
            r = requests.put(link,
                             headers={'Content-Type': 'application/json',
                                      'authorization': self.token},
                             json=json_admin_data).json()
            return r
        except Exception:
            raise Exception('Something went wrong, impossible to block courier')

    def courier_disable(self, courier_id, reason):
        try:
            json_admin_data = {
                "status": "DISABLED",
                "statusReason": reason
            }
            # post updated info
            link = 'https://adminapi.glovoapp.com/admin/couriers/' + str(courier_id) + '/secondary_settings'
            r = requests.put(link,
                             headers={'Content-Type': 'application/json',
                                      'authorization': self.token},
                             json=json_admin_data).json()
            return r
        except Exception:
            raise Exception('Can\'t disable courier')
