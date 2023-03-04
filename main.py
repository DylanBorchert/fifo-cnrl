# import extention for api requests
import requests
import json
import pprint
import functools
import re


front_window_seat_weight = 0.8
back_window_seat_weight = 1
blinded_by_light_weight = 0.1
front_better_window_weight = 1
back_better_window_weight = 1
closer_to_front = 0.003 # per seat
asile_seat_weight = 1
leg_room_weight = 0
sec1_weight = 0.1 #sections 2-5
sec2_weight = 0.1 #sections 6-10
sec3_weight = 0.05 #setion 11-12
sec4_weight = 0.1 #sections 13-18
sec5_weight = 1.5 #sections 19-23
seat_empty_beside = 2.5

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
    if seatNumber >= 13 and (seatLetter == "A" or seatLetter == "F") and seatNumber % 2 == 1:
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
        points -= sec5_weight

    if (seatLetter == "A" or seatLetter == "C") and get_seat_satus(str(seatNumber)+"B", seatlist) == 0:
        points += seat_empty_beside
    if (seatLetter == "D" or seatLetter == "F") and get_seat_satus(str(seatNumber)+"E", seatlist) == 0:
        points += seat_empty_beside

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
                 'xParameters': '{"xStatus":1,"xReturnQuantity":9999,"xEmployee_ID":"1121972","xStartDate":null,"xEndDate":null}'}

profileResp = requests.get(
    'https://cnrl-cirysm-api.ccihive.com/api/v1/Uew/Get', params=profileParams)

json_data = json.loads(profileResp.text)


allBookings = json.loads(json_data["xData"])["XBYL"]

flights = [x for x in allBookings if x["xType"] == "Charter"]

camps = [x for x in allBookings if x["xType"] == "Camp"]

for index in range(1):
    index = 5
    FromLocation = flights[index]["xFromLocation"]
    ToLocation = flights[index]["xToLocation"]
    StartDate = flights[index]["xStartDate"]
    flightID = flights[index]["xGUID"]
    seatCode = flights[index]["xSeatRoomCode"]

    flightParams = {'xSid': 123, 'xCode': 'SYSAME019', 'xGUID': '',
                    'xParameters': '{"xGUID":"'+flightID+'"}'}

    flightResp = requests.get(
        'https://cnrl-cirysm-api.ccihive.com/api/v1/Uew/Get', params=flightParams)

    seats = json.loads(json.loads(flightResp.text)["xData"])["XBYL"]
    
    seats = sorted(seats, key=functools.cmp_to_key(compare) )

    for seat in seats:
        if seat["xSeat"] == seatCode:
            seat["xSeatStatus"] = 0

    allSeats = [{"Seat": s["xSeat"], "SeatStatus": s["xSeatStatus"], "points": score_seat(s["xSeat"],s["xSeatStatus"],seats)} for s in seats]
    
            
    openSeats = [x for x in allSeats if x["SeatStatus"] == 0]
    
    
    bestSeat = max(openSeats, key=lambda x:x['points'])

    print(f'{FromLocation} - {ToLocation} | Date: {StartDate} | current seat is {seatCode} and has {len(openSeats)} open seats : {flightID} | best seat is {bestSeat["Seat"]} with {bestSeat["points"]} points')

    draw_plane(allSeats)


