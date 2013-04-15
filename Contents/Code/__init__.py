####################################################################################################
TITLE = "Food Network Canada"
ART = 'art-default.jpg'
ICON = 'icon-default.png'
FOOD_PARAMS         = ["6yC6lGVHaVA8oWSm1F9PaIYc9tOTzDqY", "z/FOODNET%20Player%20-%20Video%20Centre"]
FEED_LIST = "http://feeds.theplatform.com/ps/JSON/PortalService/2.2/getCategoryList?PID=%s&startIndex=1&endIndex=500&query=hasReleases&query=CustomText|PlayerTag|%s&field=airdate&field=fullTitle&field=author&field=description&field=PID&field=thumbnailURL&field=title&contentCustomField=title&field=ID&field=parent"
FEEDS_LIST = "http://feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?field=ID&field=contentID&field=PID&field=URL&field=airdate&PID=%s&contentCustomField=Episode&contentCustomField=Season&query=CategoryIDs|%s&field=thumbnailURL&field=title&field=length&field=description&startIndex=1&endIndex=500&sortField=airdate&sortDescending=true"
DIRECT_FEED = "http://release.theplatform.com/content.select?format=SMIL&pid=%s&UserName=Unknown&Embedded=True"

IGNORED = ["FOODNETVC", "Most Recent", "Video Blogs", "Video Bites", "FOODNETHOST"] # ' "Web Exclusives"

###################################################################################################
def Start():
    # Setup the default attributes for the ObjectContainer
    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)
    
    # Setup the default attributes for the other objects
    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    EpisodeObject.thumb = R(ICON)
    EpisodeObject.art = R(ART)

    HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
@handler("/video/food_network_canada", TITLE, ICON, ART)
def MainMenu():
    oc = ObjectContainer()
    network = FOOD_PARAMS

    content = JSON.ObjectFromURL(FEED_LIST % (network[0], network[1]))
    showList = {}
    shows = []
    shows_with_seasons = []

    items = content['items']

    for item in items:
        if item['parent'] == '':
            continue
        elif "/Web Exclusives/" in item['parent']:
            continue
        else: pass
    
        title = item['parent'].split('/')[-1]
        if title in IGNORED:
            continue
        elif title == 'Food Network Classics':
            title = item['title']
        elif title == "TV Shows":
            title = item['title']
        else:
            pass
        
        item_id = item['ID']
        thumb = item['thumbnailURL']

        if title in shows:
            if title in shows_with_seasons:
                continue
            else:
                oc.add(DirectoryObject(key=Callback(SeasonsPage, network=network, showtitle=title), title=title))
                showList[title] = False
                shows_with_seasons.append(title)
        else:
            shows.append(title)
            showList[title] = {'title':title, 'id':item_id}
    
    for show in shows:
        if showList[show]:
            oc.add(DirectoryObject(key=Callback(VideosPage, pid=network[0], iid=showList[show]['id'], show=showList[show]['title']), title=showList[show]['title']))
        else:
            continue
    
    oc.objects.sort(key = lambda obj: obj.title)
    return oc

####################################################################################################
def VideosPage(pid, iid, show):
    oc = ObjectContainer()
    pageURL = FEEDS_LIST % (pid, iid)
    feeds = JSON.ObjectFromURL(pageURL)
    
    showList = {}
    
    for item in feeds['items']:
        title = item['title']
        try:
            # show exists, skip adding multiples
            if showList[title]:
                continue
        except:
            # show doesn't exist, add it
            showList[title]=""
            pid = str(item['PID'])
            iid = str(item['contentID'])
            url = "http://www.foodnetwork.ca/video/video.html?v="+iid+"#video"
            summary =  item['description']
            duration = item['length']
            thumb_url = item['thumbnailURL']
            airdate = int(item['airdate'])/1000
            originally_available_at = Datetime.FromTimestamp(airdate).date()
                        
            try:
                # try to set the seasons and episode info
                season = item['contentCustomData'][1]['value']
                seasonint = int(float(season))
                episode = item['contentCustomData'][0]['value']
                episodeint = int(float(episode))
                oc.add(
                    EpisodeObject(
                        url = url,
                        title = title,
                        summary=summary,
                        duration=duration,
                        thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON),
                        originally_available_at = originally_available_at,
                        season = seasonint,
                        index = episodeint
                        )
                    )

            except:
                # if we don't get the season/episode info then don't set it
                oc.add(
                    EpisodeObject(
                        url = url,
                        title = title,
                        summary=summary,
                        duration=duration,
                        thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON),
                        originally_available_at = originally_available_at
                        )
                    )
    
    return oc

####################################################################################################
def SeasonsPage(network, showtitle):

    oc = ObjectContainer()
    
    pageURL = FEED_LIST % (network[0], network[1])
    content = JSON.ObjectFromURL(pageURL)
    season_list = []
    
    for item in content['items']:
        if showtitle in item['fullTitle']:
            title = item['fullTitle'].split('/')[-1]
            if title not in season_list and title != showtitle:
                season_list.append(title)
                iid = item['ID']
                thumb_url = item['thumbnailURL']
                oc.add(
                    DirectoryObject(
                        key = Callback(VideosPage, pid=network[0], iid=iid, show=showtitle),
                            title = title,
                            thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
                            )
                        )
        
    oc.objects.sort(key = lambda obj: obj.title)
    return oc