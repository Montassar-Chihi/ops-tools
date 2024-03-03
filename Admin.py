import pandas as pd
import requests


class Admin:

    def __init__(self, token, refresh_token):
        self.token = token
        self.refresh_token = refresh_token

    def rebook_kickedout_couriers(self, file=None, courier_id=None, slot_id=None):
        if (courier_id is None) and (slot_id is None):
            df = pd.read_csv(file)

            for index, row in df.iterrows():
                courier_id = row["courier_id"]
                slot_id = row["slot_id"]
                self.unbook_slot(courier_id, slot_id)
                r = self.book_slot(courier_id, slot_id)
                print("courier_id: ", courier_id, "slot_id: ", slot_id, "successful booking: ", r)
        else:
            self.unbook_slot(courier_id, slot_id)
            r = self.book_slot(courier_id, slot_id)
            print("courier_id: ", courier_id, "slot_id: ", slot_id, "successful booking: ", r)

    def setup_new_couriers_profiles(self):
        new_couriers = pd.read_csv("data/Fleet Overview - TIS - Formation.csv")
        new_couriers = new_couriers[new_couriers["courier_id"].isna() == False]
        for index, courier_data in new_couriers.iterrows():
            courier_id = int(courier_data["courier_id"])
            new_bag_tag = 1417
            threepl_tag = courier_data["threepl_tag_id"]
            threepl_id = courier_data["threepl_id"]
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

            self.add_tags(courier_id, [new_bag_tag,threepl_tag])
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
            print("courier_id: ", courier_id, "slot_id: ", slot_id, "successful booking: ", r)

    def add_invoicing_details(self, courier_id, threepl_id, threepl_iban, vat_number):
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
        print(tags_old_json)
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
