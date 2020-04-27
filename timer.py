import schedule
import time


#https://pypi.org/project/schedule/
def update():

    ##RESETS SPOTS LEFT 
    # gets ID of all shifts 
     shift_ids = requests.get("http://localhost:5000/resetmaxemployeesids)
    # for each ID, gets shift information
    shift_ids = shift_ids.json()
    # for each request, get information
    for i in range(len(shift_ids)):
        id_shift = str(shift_ids[i]["id_shift"])
        #resets max num of employees for each id_shift
        resetMax = requests.post("http://localhost:5000/resetmaxemployees/" + id_shift)
    
    print("it's 4:44")

    ##UPDATES DATES IN DATABASE 
    updateDates = requests.post("http://localhost:5000/updateshiftdates")


#Every thursday at 8:00 am will update DB and spots left 
schedule.every().thursday.at("18:14").do(update)

# Loop so that the scheduling task keeps on running at all time. 
while True: 
    # Checks whether a scheduled task  
    # is pending to run or not 
    schedule.run_pending() 
    time.sleep(60)