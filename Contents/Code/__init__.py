import re, string, datetime, operator

####################################################################################################

VIDEO_PREFIX = "/video/greattv.ca"

NAME = L('Title')

ART             = 'art-default.png'
ICON            = 'icon-default.png'
DIY_ICON        = 'Diy-icon.png'
DIY_ART         = 'Diy-art.png'
FOOD_ICON       = 'Food-icon.png'
FOOD_ART        = 'Food-art.png'
GLOBAL_ICON     = 'Global-icon.png'
GLOBAL_ART      = 'Global-art.png'
HGTV_ICON       = 'HGTV-icon.png'
HGTV_ART        = 'HGTV-art.png'
HISTORY_ICON    = 'History-icon.png'
HISTORY_ART     = 'History-art.png'
SHOWCASE_ICON   = 'Showcase-icon.png'
SHOWCASE_ART    = 'Showcase-art.png'
SLICE_ICON      = 'Slice-icon.png'
SLICE_ART       = 'Slice-art.png'
TVTROPOLIS_ICON = 'TVTropolis-icon.png'
TVTROPOLIS_ART  = 'TVTropolis-art.png'

DIY_PARAMS          = ["FgLJftQA35gBSx3kKPM46ZVvhP6JxTYt", "z/DIY%20Network%20-%20Video%20Centre"]
FOOD_PARAMS         = ["6yC6lGVHaVA8oWSm1F9PaIYc9tOTzDqY", "z/FOODNET%20Player%20-%20Video%20Centre"]
GLOBALTV_PARAMS     = ["W_qa_mi18Zxv8T8yFwmc8FIOolo_tp_g", "z/Global%20Video%20Centre"]
HGTV_PARAMS         = ["HmHUZlCuIXO_ymAAPiwCpTCNZ3iIF1EG", "z/HGTV%20Player%20-%20Video%20Center"]
HISTORY_PARAMS      = ["IX_AH1EK64oFyEbbwbGHX2Y_2A_ca8pk", "z/History%20Player%20-%20Video%20Center"]
SHOWCASE_PARAMS     = ["sx9rVurvXUY4nOXBoB2_AdD1BionOoPy", "z/Showcase%20Video%20Centre"]
SLICE_PARAMS        = ["EJZUqE_dB8XeUUgiJBDE37WER48uEQCY", "z/Slice%20Player%20-%20New%20Video%20Center"]
TVTROPOLIS_PARAMS   = ["3i9zvO0c6HSlP7Fz848a0DvzBM0jUWcC", "z/TVTropolis%20Player%20-%20Video%20Center"]

FEED_LIST    = "http://feeds.theplatform.com/ps/JSON/PortalService/2.2/getCategoryList?PID=%s&startIndex=1&endIndex=500&query=hasReleases&query=CustomText|PlayerTag|%s&field=airdate&field=fullTitle&field=author&field=description&field=PID&field=thumbnailURL&field=title&contentCustomField=title&field=ID&field=parent"

FEEDS_LIST    = "http://feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=%s&startIndex=1&endIndex=500&query=categoryIDs|%s&query=BitrateEqualOrGreaterThan|400000&query=BitrateLessThan|601000&sortField=airdate&sortDescending=true&field=airdate&field=author&field=description&field=length&field=PID&field=thumbnailURL&field=title&contentCustomField=title"
    
DIRECT_FEED = "http://release.theplatform.com/content.select?format=SMIL&pid=%s&UserName=Unknown&Embedded=True&TrackBrowser=True&Tracking=True&TrackLocation=True"

####################################################################################################

def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, L('VideoTitle'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)


####################################################################################################
def MainMenu():
    dir = MediaContainer(viewGroup="List")
    dir.Append(Function(DirectoryItem(DiyPage, "diy Network", thumb=R(DIY_ICON), art=R(DIY_ART)), network = DIY_PARAMS))
    dir.Append(Function(DirectoryItem(FoodPage, "Food Network", thumb=R(FOOD_ICON), art=R(FOOD_ART)), network = FOOD_PARAMS))
    dir.Append(Function(DirectoryItem(GlobalPage, "Global TV", thumb=R(GLOBAL_ICON), art=R(GLOBAL_ART)), network = GLOBALTV_PARAMS))
    dir.Append(Function(DirectoryItem(HGTVPage, "HGTV", thumb=R(HGTV_ICON), art=R(HGTV_ART)), network = HGTV_PARAMS))
    dir.Append(Function(DirectoryItem(HistoryPage, "History", thumb=R(HISTORY_ICON), art=R(HISTORY_ART)), network = HISTORY_PARAMS))
    dir.Append(Function(DirectoryItem(ShowcasePage, "Showcase", thumb=R(SHOWCASE_ICON), art=R(SHOWCASE_ART)), network = SHOWCASE_PARAMS))
    dir.Append(Function(DirectoryItem(HistoryPage, "Slice", thumb=R(SLICE_ICON), art=R(SLICE_ART)), network = SLICE_PARAMS))
    dir.Append(Function(DirectoryItem(TvtropolisPage, "TVTropolis", thumb=R(TVTROPOLIS_ICON), art=R(TVTROPOLIS_ART)), network = TVTROPOLIS_PARAMS))
    return dir
    
####################################################################################################
def VideoPlayer(sender, pid):
    videosmil = HTTP.Request(DIRECT_FEED % pid).content
    player = videosmil.split("ref src")
    player = player[2].split('"')
    #Log(player)
    if ".mp4" in player[1]:
        player = player[1].replace(".mp4", "")
        try:
            clip = player.split(";")
            clip = "mp4:" + clip[4]
        except:
            clip = player.split("/video/")
            player = player.split("/video/")[0]
            clip = "mp4:/video/" + clip[-1]
    else:
        player = player[1].replace(".flv", "")
        try:
            clip = player.split(";")
            clip = clip[4]
        except:
            clip = player.split("/video/")
            player = player.split("/video/")[0]
            clip = "/video/" + clip[-1]
    #Log(player)
    #Log(clip)
    return Redirect(RTMPVideoItem(player, clip))
    
####################################################################################################
def VideosPage(sender, pid, id):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="InfoList", art=sender.art)
    pageUrl = FEEDS_LIST % (pid, id)
    feeds = JSON.ObjectFromURL(pageUrl)
    #Log(feeds)
    for item in feeds['items']:
        title = item['title']
        pid = item['PID']
        summary =  item['description'].replace('In Full:', '')
        duration = item['length']
        thumb = item['thumbnailURL']
        airdate = int(item['airdate'])/1000
        subtitle = 'Originally Aired: ' + datetime.datetime.fromtimestamp(airdate).strftime('%a %b %d, %Y')
        dir.Append(Function(VideoItem(VideoPlayer, title=title, subtitle=subtitle, summary=summary, thumb=thumb, duration=duration), pid=pid))
    
    dir.Sort('title')
    return dir
    
#def ClipsPage(sender, showname):
    #dir = MediaContainer(title2=sender.itemTitle, viewGroup="InfoList")
    #dir.Append(Function(DirectoryItem(VideosPage, "Full Episodes"), clips="episode", showname=showname))
    #dir.Append(Function(DirectoryItem(VideosPage, "Clips"), clips="", showname=showname))
    #return dir
####################################################################################################
def FoodPage(sender, network):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="List", art=sender.art)
    content = RSS.FeedFromURL("http://www.foodnetwork.ca/2086977.atom")
    #Log(content)
    for item in content['entries']:
        title = item['title']
        id = item['link'].split('=')[1]
        dir.Append(Function(DirectoryItem(VideosPage, title), pid=network[0], id=id))
    return dir

####################################################################################################
def GlobalPage(sender, network):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="List", art=sender.art)
    content = JSON.ObjectFromURL(FEED_LIST % (network[0], network[1]))
    for item in content['items']:
        if item['title'] == "Full Episodes":
            title = item['fullTitle']
            title = title.split('/')[2]
            id = item['ID']
            dir.Append(Function(DirectoryItem(VideosPage, title), pid=network[0], id=id))
    return dir
    
####################################################################################################

def HGTVPage(sender, network):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="List", art=sender.art)
    content = JSON.ObjectFromURL(FEED_LIST % (network[0], network[1]))
    for item in content['items']:
        if "Full Episodes" in item['parent']:
            title = item['title']
            id = item['ID']
            thumb = item['thumbnailURL']
            dir.Append(Function(DirectoryItem(VideosPage, title, thumb=thumb), pid=network[0], id=id))
    return dir
    
####################################################################################################
def HistoryPage(sender, network):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="List", art=sender.art)
    content = JSON.ObjectFromURL(FEED_LIST % (network[0], network[1]))
    showList = {}
    showCount = 0
    #items = sorted(content['items'], key=attrgetter('fullTitle'))
    items = content['items']
    #Log(items)
    items.sort(key=operator.itemgetter('fullTitle'))
    #Log(items)
    #parent = ""
    for item in items:
        if "Full Episodes" in item['fullTitle']:
            title = item['fullTitle']
            title = title.split('/')[1]
            id = item['ID']
            thumb = item['thumbnailURL']
            #dir.Append(Function(DirectoryItem(VideosPage, title, thumb=thumb), pid=network[0], id=id))
            try:
                if showList[title]:
                    discard = dir.Pop(showList[title]['index'])
                    #Log('Removed: %s' %discard.title)
                    dir.Append(Function(DirectoryItem(SeasonsPage, title, thumb=sender.thumb), network=network))
                else:
                    pass
            except:
                #Log('try failed')
                #Log('showList does not contain %s' % title)
                showList[title] = {'id':id, 'index':showCount}
                showCount +=1
                dir.Append(Function(DirectoryItem(VideosPage, title, thumb=sender.thumb), pid=network[0], id=id))
    return dir
            
####################################################################################################
def ShowcasePage(sender, network):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="List", art=sender.art)
    content = JSON.ObjectFromURL(FEED_LIST % (network[0], network[1]))
    showList = {}
    showCount = 0
    #parent = ""
    items = content['items']
    items.sort(key=operator.itemgetter('fullTitle'))
    for item in items:
        if "SHOWVC/Shows/" in item['fullTitle']:
            title = item['fullTitle']
            #Log(title)
            title = title.split('/')[2]
            id = item['ID']
            #thumb = item['thumbnailURL']
            try:
                if showList[title]:
                    discard = dir.Pop(showList[title]['index'])
                    #Log('Removed: %s' %discard.title)
                    dir.Append(Function(DirectoryItem(SeasonsPage, title, thumb=sender.thumb), network=network))
                else:
                    pass
            except:
                #Log('try failed')
                #Log('showList does not contain %s' % title)
                showList[title] = {'id':id, 'index':showCount}
                showCount +=1
                dir.Append(Function(DirectoryItem(VideosPage, title, thumb=sender.thumb), pid=network[0], id=id))
                
    return dir
            
####################################################################################################
def TvtropolisPage(sender, network):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="List", art=sender.art)
    content = JSON.ObjectFromURL(FEED_LIST % (network[0], network[1]))
    showList = {}
    showCount = 0
    #parent = ""
    items = content['items']
    items.sort(key=operator.itemgetter('fullTitle'))
    for item in items:
        if "SPECTVVC/" in item['fullTitle']:
            title = item['fullTitle']
            #Log(title)
            title = title.split('/')[1]
            id = item['ID']
            #thumb = item['thumbnailURL']
            try:
                if showList[title]:
                    discard = dir.Pop(showList[title]['index'])
                    #Log('Removed: %s' %discard.title)
                    dir.Append(Function(DirectoryItem(SeasonsPage, title, thumb=sender.thumb), network=network))
                else:
                    pass
            except:
                #Log('try failed')
                #Log('showList does not contain %s' % title)
                showList[title] = {'id':id, 'index':showCount}
                showCount +=1
                dir.Append(Function(DirectoryItem(VideosPage, title, thumb=sender.thumb), pid=network[0], id=id))
                
    return dir
            
####################################################################################################
def DiyPage(sender, network):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="List", art=sender.art)
    content = JSON.ObjectFromURL(FEED_LIST % (network[0], network[1]))
    #Log(content)
    showList = {}
    showCount = 0
    #parent = ""
    items = content['items']
    items.sort(key=operator.itemgetter('fullTitle'))
    for item in items:
        if "DIYVC/" in item['fullTitle']:
            title = item['fullTitle']
            #Log(title)
            title = title.split('/')[1]
            id = item['ID']
            #thumb = item['thumbnailURL']
            try:
                if showList[title]:
                    discard = dir.Pop(showList[title]['index'])
                    #Log('Removed: %s' %discard.title)
                    dir.Append(Function(DirectoryItem(SeasonsPage, title, thumb=sender.thumb), network=network))
                else:
                    pass
            except:
                #Log('try failed')
                #Log('showList does not contain %s' % title)
                showList[title] = {'id':id, 'index':showCount}
                showCount +=1
                dir.Append(Function(DirectoryItem(VideosPage, title, thumb=sender.thumb), pid=network[0], id=id))
                
    return dir
            
####################################################################################################
def SeasonsPage(sender, network):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="List", art=sender.art)
    content = JSON.ObjectFromURL(FEED_LIST % (network[0], network[1]))
    #Log(sender.itemTitle)
    #Log(content)
    for item in content['items']:
        if sender.itemTitle in item['fullTitle']:
            title = item['fullTitle']
            #Log(title)
            title = title.split('/')[-1]
            #if title == 'New This Week':
            #    title = item['title']
            id = item['ID']
            #thumb = item['thumbnailURL']
            dir.Append(Function(DirectoryItem(VideosPage, title, thumb=sender.thumb), pid=network[0], id=id))
    dir.Sort('title')
    return dir
            
####################################################################################################
















































