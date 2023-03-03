# import extention for api requests
import requests
import json
import pprint
import functools
import re


def score_seat(seatID, status, seatlist):
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
    #sections 13-18 -   -   -   +0.1    sec3_weight
    #sections 19-23 -   -   -   +0.02   sec4_weight
    return 0

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
        if re.sub(r'[0-9]', '', seatlist[index]["Seat"]) == "A":
            print('[{0:>3}] [{1:>3}] [{2:>3}]    [{3:>3}] [{4:>3}] [{5:>3}]'.format(seatlist[index]["Seat"], seatlist[index+1]["Seat"], seatlist[index+2]["Seat"], seatlist[index+3]["Seat"], seatlist[index+4]["Seat"], seatlist[index+5]["Seat"]))
        elif seatlist[index]["Seat"]== "11B":
            print('      [{0:>3}] [{1:>3}]    [{2:>3}] [{3:>3}]      '.format(seatlist[index]["Seat"], seatlist[index+1]["Seat"], seatlist[index+2]["Seat"], seatlist[index+3]["Seat"], seatlist[index+4]["Seat"]))
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

    # pprint.pprint(seats)
    
    seats = sorted(seats, key=functools.cmp_to_key(compare) )

    openSeats = [x for x in seats if x["xSeatStatus"] == 0]

    allSeats = [{"Seat": s["xSeat"], "SeatStatus": s["xSeatStatus"], "points": score_seat(s["xSeat"],s["xSeatStatus"],seats)} for s in seats]

    print(f'{FromLocation} - {ToLocation} | Date: {StartDate} | current seat is {seatCode} and has {len(openSeats)} open seats : {flightID}')


    draw_plane(allSeats)
    


