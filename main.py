# import requests library using command:
# python -m pip install requests
import requests 

#python defualts 
import json
import pprint
import functools
import re

#your user id, can get get from profile page on site
cirys_id = ''

#this will enable steat changing, enabl once you dial in your seat scoring
ENABLE_SEAT_CHANGE = False

#number of consecutive flights to check, -1 will check all
consecutive_flights = 10

#weighting for front half window seats
front_window_seat_weight = 0.8 
#weighting for back half window seats
back_window_seat_weight = 1
#seats that where you get blinded by the light
blinded_by_light_weight = 0.1
#window seats that have extra shoulder room front half of plane
front_better_window_weight = 0.3
#window seats that have extra shoulder room back half of plane
back_better_window_weight = 0.2 
#row to stop back_better_window_weight 
back_stop_point = 19
# scaling per seet closer to front
closer_to_front = 0.003
#weighting for asile seats
asile_seat_weight = 1
#leg room weight, includes row 1 and 11-12
leg_room_weight = 0
#section weights 2-5
sec1_weight = 0 
#section weights 6-10
sec2_weight = 0.1 
#setion weights 11-12
sec3_weight = 0.05 
#sections weights 13-19
sec4_weight = 0.11 
#sections 20-23
sec5_weight = 0
#weighting for empty seat beside front 
seat_empty_beside_front = 2.0
#weighting for empty seat beside back
seat_empty_beside_back = 1.0
#weighting to for middle seats (negative to avoid)
middle_seats = -2.0

def get_seat_satus(seatID, seatlist):
    for seat in seatlist:
        if seatID == seat["xSeat"]: 
                return seat["xSeatStatus"]

def score_seat(seatID, status, seatlist):
    points = 0.0 # base points
    if status != 0:
        return 0.0
    seatLetter = re.sub(r'[0-9]', '', seatID)
    seatNumber = int(re.sub(r'[A-F]', '', seatID))
    if seatNumber <= 10 and (seatLetter == "A" or seatLetter == "F"):
        points += front_window_seat_weight
    if seatNumber >= 13 and (seatLetter == "A" or seatLetter == "F"):
        points += back_window_seat_weight

    if seatNumber <= 10 and (seatLetter == "A" or seatLetter == "F") and seatNumber % 2 == 0:
        points += front_better_window_weight
    if (seatNumber >= 13 and (seatLetter == "A" or seatLetter == "F") and seatNumber % 2 == 1) and seatNumber <= back_stop_point:
        points += back_better_window_weight

    if seatLetter == "A" or seatLetter == "C" or seatLetter == "F":
        points += blinded_by_light_weight

    if seatLetter == "C" or seatLetter == "D":
        points += asile_seat_weight

    if seatNumber == 1 or seatNumber == 11 or seatNumber == 12:
        points += leg_room_weight
    if seatNumber <= 5 and seatNumber > 1:
        points += sec1_weight
    if seatNumber <= 10 and seatNumber > 5:
        points += sec2_weight
    if seatNumber <= 13 and seatNumber > 10:
        points += sec3_weight
    if seatNumber <= 19 and seatNumber > 13:
        points += sec4_weight
    if seatNumber <= 23 and seatNumber > 19:
        points += sec5_weight
        
    if seatLetter == "B" or seatLetter == "E":
        points += middle_seats

    if (seatLetter == "A" or seatLetter == "C") and get_seat_satus(str(seatNumber)+"B", seatlist) == 0:
        if seatNumber <= 10:
            points += seat_empty_beside_front
        elif seatNumber <= back_stop_point:
            points += seat_empty_beside_back
    if (seatLetter == "D" or seatLetter == "F") and get_seat_satus(str(seatNumber)+"E", seatlist) == 0:
        if seatNumber <= 10:
            points += seat_empty_beside_front
        elif seatNumber <= back_stop_point:
            points += seat_empty_beside_back

    row_multiplier = (23 - seatNumber ) * closer_to_front
    points += row_multiplier

    return points

def compare(item1, item2):
    # sort by row
    seat1_row = int(re.sub(r'[A-F]', '', item1["xSeat"]))
    seat2_row = int(re.sub(r'[A-F]', '', item2["xSeat"]))
    if seat1_row > seat2_row:
        return 1
    elif seat1_row < seat2_row:
        return -1
    else:
        return 0
    
def draw_plane(seatlist):
    for index in range(len(seatlist)):
        if index < len(seatlist) - 5:
            row_num = re.sub(r'[A-F]', '', seatlist[index]["Seat"])
            a = "" if seatlist[index]["points"] == 0 else str('{0:>5.2f}'.format(float(seatlist[index]["points"])))
            b = "" if seatlist[index+1]["points"] == 0 else str('{0:>5.2f}'.format(float(seatlist[index+1]["points"])))
            c = "" if seatlist[index+2]["points"] == 0 else str('{0:>5.2f}'.format(float(seatlist[index+2]["points"])))
            d = "" if seatlist[index+3]["points"] == 0 else str('{0:>5.2f}'.format(float(seatlist[index+3]["points"])))
            e = "" if seatlist[index+4]["points"] == 0 else str('{0:>5.2f}'.format(float(seatlist[index+4]["points"])))
            f = "" if seatlist[index+5]["points"] == 0 else str('{0:>5.2f}'.format(float(seatlist[index+5]["points"])))
        
            if re.sub(r'[0-9]', '', seatlist[index]["Seat"]) == "A":
                print('{0:>2} [{1:>5}] [{2:>5}] [{3:>5}]    [{4:>5}] [{5:>5}] [{6:>5}]'.format(row_num, a, b, c, d, e, f))
            elif seatlist[index]["Seat"]== "11B":
                print('{0:>2}         [{1:>5}] [{2:>5}]    [{3:>5}] [{4:>5}]      '.format(row_num, a, b, c, d))
            else:
                continue
        

profileParams = {'xSid': 123, 'xCode': 'SYSAME001', 'xGUID': '',
                 'xParameters': '{"xStatus":1,"xReturnQuantity":9999,"xEmployee_ID":' + cirys_id + ',"xStartDate":null,"xEndDate":null}'}

profileResp = requests.get(
    'https://cnrl-cirysm-api.ccihive.com/api/v1/Uew/Get', params=profileParams)

json_data = json.loads(profileResp.text)


allBookings = json.loads(json_data["xData"])["XBYL"]

flights = [x for x in allBookings if x["xType"] == "Charter"]

camps = [x for x in allBookings if x["xType"] == "Camp"]



if consecutive_flights == -1: 
    num_flights = len(flights) 
else: 
    num_flights = consecutive_flights

for index in range(num_flights):
    FromLocation = flights[index]["xFromLocation"]
    ToLocation = flights[index]["xToLocation"]
    StartDate = flights[index]["xStartDate"]
    flightKey = flights[index]["xGUID"]
    seatCode = flights[index]["xSeatRoomCode"]

    flightParams = {'xSid': 123, 'xCode': 'SYSAME019', 'xGUID': '',
                    'xParameters': '{"xGUID":"'+flightKey+'"}'}

    flightResp = requests.get(
        'https://cnrl-cirysm-api.ccihive.com/api/v1/Uew/Get', params=flightParams)

    seats = json.loads(json.loads(flightResp.text)["xData"])["XBYL"]
    
    seats = sorted(seats, key=functools.cmp_to_key(compare))

    for seat in seats:
        if seat["xSeat"] == seatCode:
            seat["xSeatStatus"] = 0

    allSeats = [{"Seat": s["xSeat"], "SeatStatus": s["xSeatStatus"], "points": score_seat(s["xSeat"],s["xSeatStatus"],seats)} for s in seats]
    
    if index == 0:
        print('-----------------SEAT SCORING ALL SEATS--------------')
        draw_plane([{"Seat": s["xSeat"], "SeatStatus": 0, "points": score_seat(s["xSeat"],0,[{"xSeat": s["xSeat"], "xSeatStatus": 0} for x in seats])} for s in seats])
        print('-----------------------------------------------------')
            
    openSeats = [x for x in allSeats if x["SeatStatus"] == 0]
    
    
    bestSeat = max(openSeats, key=lambda x:x['points'])
    
    print(f'{FromLocation} - {ToLocation} | Date: {StartDate} | current seat is {seatCode} and has {len(openSeats)} open seats : {flightKey} | best seat is {bestSeat["Seat"]} with {bestSeat["points"]} points')
    
    if bestSeat["Seat"] != seatCode and ENABLE_SEAT_CHANGE:
        print("################################ SEAT CHANGED ################################")
    
    
        selectSeatParams = {'xSid': 123, 'xCode': 'SYSAME020', 'xGUID': '',
                        'xParameters': '{"xLoginID":'+ cirys_id +',"xNewSeat":"'+str(bestSeat["Seat"])+'","xGUID":"'+str(flightKey)+'"}'}

        selectSeatResp = requests.get(
            'https://cnrl-cirysm-api.ccihive.com/api/v1/Uew/Get', params=selectSeatParams)

        print(json.loads(json.loads(selectSeatResp.text)["xData"])["XBYL"][0]["xMessage"] + f' | from current seat is {seatCode} to {bestSeat["Seat"]}')
        print(f' | from current seat is {seatCode} to {bestSeat["Seat"]}')
        draw_plane(allSeats)
        print("##############################################################################")
        rankedSteats = sorted(openSeats, key=lambda x: x['points'], reverse=True)
        for i in range(5):
            print(f'{rankedSteats[i]["Seat"]} with {rankedSteats[i]["points"]:2f} points')
    else:
        print("- - - - - - - - - - - - - - - - - KEEP SEAT  - - - - - - - - - - - - - - - - -")
        rankedSteats = sorted(openSeats, key=lambda x: x['points'], reverse=True)
        for i in range(5):
            print(f'{rankedSteats[i]["Seat"]} with {rankedSteats[i]["points"]:2f} points')
    print('----------------------------------------------------------------------------------------------------------------')




