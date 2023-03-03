# import extention for api requests
import requests
import json
import pprint
import functools
import re


window_seat_weight = 1.7
blinded_by_light_weight = 0.15
better_window_weight = 0.4
middle_taken_beside_weight = -1.0
closer_to_front = 0.005 # per seat
asile_seat_weight = 1.3
leg_room_weight = 0.05
sec1_weight = 0.01 #sections 2-5
sec2_weight = 0.1 #sections 6-10
sec3_weight = 0.1 #setion 11-12
sec4_weight = 0.15 #sections 13-18
sec5_weight = -0.5 #sections 19-23


    # prefered seat point system
    # A or F -  -   -   -   -   +1.5    window_seat_weight
    # A-C   -   -   -   -   -   +0.5    left_side_weight
    # <= 10 A or F Even Seat    +1.0    better_window_weight
    # >=13 A or F ODD Seat      +1.0    
    # B taken beside A  -   -   -1.0    middle_taken_beside_weight
    # E taken beside F  -   -   -1.0    
    # closer to front points    +0.01/per start at back going to front      closer_to_front
    # C or D    -   -   -   -   +1.0    asile_seat_weight
    # taken     -   -   -   -   =0
    #sections 2-5   -   -   -   +0.05   sec1_weight
    #sections 6-10  -   -   -   +0.15   sec2_weight
    #setion 11-12   -   -   -   +0.1    sec3_weight
    #sections 13-18 -   -   -   +0.1    sec4_weight
    #sections 19-23 -   -   -   +0.02   sec5_weight
def score_seat(seatID, status, seatlist):
    points = 0.0 # base points
    seatLetter = re.sub(r'[0-9]', '', seatID)
    seatNumber = int(re.sub(r'[A-F]', '', seatID))
    if seatLetter == "A" or seatLetter == "F":
        points += window_seat_weight
    if seatLetter == "A" or seatLetter == "B" or seatLetter == "C" or seatLetter == "F":
        points += blinded_by_light_weight
    if (seatNumber <= 10 and (seatLetter == "A" or seatLetter == "F") and seatNumber % 2 == 0) or (seatNumber >= 13 and (seatLetter == "A" or seatLetter == "F") and seatNumber % 2 == 1):
        points += better_window_weight
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
    
    
    row_multiplier = (23 - seatNumber ) * closer_to_front
    points += row_multiplier
    if status != 0:
        points = 0.0
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
        row_num = re.sub(r'[A-F]', '', seatlist[index]["Seat"])
        if index < len(seatlist) - 5:
            a = float(seatlist[index]["points"])
            b = float(seatlist[index+1]["points"])
            c = float(seatlist[index+2]["points"])
            d = float(seatlist[index+3]["points"])
            e = float(seatlist[index+4]["points"])
            f = float(seatlist[index+5]["points"])
        
            if re.sub(r'[0-9]', '', seatlist[index]["Seat"]) == "A":
                print('{0:>2} [{1:>5.2f}] [{2:>5.2f}] [{3:>5.2f}]    [{4:>5.2f}] [{5:>5.2f}] [{6:>5.2f}]'.format(row_num, a, b, c, d, e, f))
            elif seatlist[index]["Seat"]== "11B":
                print('{0:>2}         [{1:>5.2f}] [{2:>5.2f}]    [{3:>5.2f}] [{4:>5.2f}]      '.format(row_num, a, b, c, d))
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

for index in range(10):
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


