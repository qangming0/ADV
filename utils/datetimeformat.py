import datetime
import dateutil.parser


def dtmValidate(date_text):
    isValid = True
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        validate = True
    except ValueError:
        validate = False
    finally:
        return isValid


def orderDursationASC(lstDur, format="%Y-%m-%d %H:%M:%S"):
    if not isinstance(lstDur, list):
        return []
    else:
        for duration in lstDur:
            duration['start'] = datetime.datetime.strptime(duration['start'], format).time()
            duration['end'] = datetime.datetime.strptime(duration['end'], format).time()
            # FIXME: fix now
            # if end < start:
            #     end = end + datetime.timedelta(days=1)

        __len = len(lstDur)
        for i in range(__len - 1):
            for j in range(i + 1, __len):
                start_i = lstDur[i]['start']
                start_j = lstDur[j]['start']
                if start_i > start_j:
                    temp = lstDur[i]
                    lstDur[i] = lstDur[j]
                    lstDur[j] = temp
                else:
                    continue

        # Cause for json encode to match
        for duration in lstDur:
            duration['start'] = str(duration['start'])
            duration['end'] = str(duration['end'])
        return lstDur

def date2str(date, format='%Y-%m-%d'):
    try:
        res = date.strftime(format)
        return res
    except:
        return None

def str2DateTime(sTime, sFormat='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.strptime(sTime, sFormat)

def changeDateTimeFormat(sTime, sFormat='%Y-%m-%d %H:%M:%S'):
    timeTmp = dateutil.parser.parse(sTime)
    return timeTmp.strftime(sFormat)