import datetime

# Utils to handle timelines in transcript file for plotting

def getVals(dic, speaker, key):
    # returns all values in the speaker dic
    vals = []
    for d in dic[speaker]:
        vals.append(d[key])
    return vals

def convertTiMs(time):
    hours, minutes, seconds = (["0", "0"] + time.split(":"))[-3:]
    m = time.split('.')[-1]
    hours = int(hours)
    minutes = int(minutes)
    seconds = float(seconds)
    miliseconds = int(3600000 * hours + 60000 * minutes + 1000 * seconds)
    return miliseconds + int(m) * 10


def convertToMss(times):
    res = []
    for time in times:
        res.append(convertTiMs(time))
    return res

def convertMsToFMT(ms):
    return str(datetime.timedelta(milliseconds=ms)).split('.')[0]


def filterSentiment(x, y):
    # filter the data by deleting the 0 sentiment scores; y = sentiment scores
    while 0.0 in y:
        index = y.index(0.0)
        x.pop(index)
        y.pop(index)

if __name__ == "__main__":
    s = convertMsToFMT(3600000 * 2 + 132130 * 2 + 23003)
    print(s)