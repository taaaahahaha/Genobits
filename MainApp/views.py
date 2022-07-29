from django.shortcuts import render
from django.http import HttpResponse
from .models import Data
from django.core.files.storage import default_storage
import csv
import json
from django.conf import settings
from wsgiref.util import FileWrapper
import mimetypes
import urllib 
import os

def index(request):
    # return HttpResponse("Hello")

    if request.method == 'POST': 
        
        f = request.FILES['file']
        timeframe = request.POST['timeframe']
        file_name = default_storage.save(f.name, f)
        print("Filename:",file_name)
        print("Timeframe:",timeframe)


        converted_filename = convert(file_name,timeframe)
        print("Converted Filename:",converted_filename)
        new_fname_location = f"{converted_filename}"
        # new_fname_location = f"{settings.MEDIA_ROOT}{file_name}"


        context = {
            'filename':file_name,
            'timeframe':timeframe,
            'convertedfile':new_fname_location,
            'all':Data.objects.all()
        }
        Data(filename=file_name,timeframe=timeframe,convertedfile_location=converted_filename).save()

        return render(request, 'MainApp/download.html', context=context)


    context = {}
    return render(request, 'MainApp/index.html', context=context)


def download(request,file_name):
    file_path = settings.MEDIA_ROOT +'/'+ file_name
    file_wrapper = FileWrapper(open(file_path,'rb'))
    file_mimetype = mimetypes.guess_type(file_path)
    response = HttpResponse(file_wrapper, content_type=file_mimetype )
    response['X-Sendfile'] = file_path
    response['Content-Length'] = os.stat(file_path).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % file_name
    return response


def convert(fname,timeframe):   
    
    path = default_storage.url(fname)[1:]

    class Candle:
        def __init__(self,BANKNIFTY,DATE,TIME,OPEN,HIGH,LOW,CLOSE,VOLUME):
            self.id = DATE+TIME.replace(':','')   # Unique in every record
            self.BANKNIFTY = BANKNIFTY 
            self.DATE = DATE 
            self.TIME = TIME 
            self.OPEN = OPEN 
            self.HIGH = HIGH 
            self.LOW = LOW 
            self.CLOSE = CLOSE 
            self.VOLUME = VOLUME 

    li_objects = []
    with open(path, 'r') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            candle_object = Candle(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            li_objects.append(candle_object)

    i=0
    solution_list = []

    while i<len(li_objects):
        
        if i%int(timeframe) == 0:
            BANKNIFTY = li_objects[i].BANKNIFTY
            DATE = li_objects[i].DATE
            TIME = li_objects[i].TIME
            OPEN = li_objects[i].OPEN

            HIGH = li_objects[i].HIGH
            LOW = li_objects[i].LOW

        elif (i+1)%int(timeframe) == 0:
            CLOSE = li_objects[i].CLOSE
            VOLUME = li_objects[i].VOLUME

            ans = Candle(BANKNIFTY,DATE,TIME,OPEN,HIGH,LOW,CLOSE,VOLUME)
            solution_list.append(ans)

            BANKNIFTY = None
            DATE = None
            TIME = None
            OPEN = None
            HIGH = None
            LOW = None
            CLOSE = None
            VOLUME = None


        else:
            temp_high = li_objects[i].HIGH
            temp_low = li_objects[i].LOW
            if temp_high > HIGH:
                HIGH = temp_high
            if temp_low < LOW:
                LOW = temp_low

        i+=1


    if i == len(li_objects):                              # Taking care of Edge Case Scenario
        if CLOSE == None and VOLUME == None:              # If timeframe is not divisible by number of records, the last candle is made by remaining left candles.
            if BANKNIFTY != None:
                CLOSE = li_objects[i-1].CLOSE
                VOLUME = li_objects[i-1].VOLUME

                ans = Candle(BANKNIFTY,DATE,TIME,OPEN,HIGH,LOW,CLOSE,VOLUME)
                solution_list.append(ans)
                


    # for i in solution_list:
    #     print(i)
    # print(len(solution_list))

    d = dict()
    for i in solution_list:
        key = i.id
        value = json.dumps(i.__dict__)
        d[key] = value
    
    new_fname = f"{fname.split('.')[0]}_converted.json"
    new_fname_location = f"{settings.MEDIA_ROOT}{new_fname}"
    # print("New filelocation",new_fname_location)
    
    out_file = open(new_fname_location, "w")
    json.dump(d, out_file, indent = 6)
    out_file.close()

    # print(out_file)
    return new_fname
