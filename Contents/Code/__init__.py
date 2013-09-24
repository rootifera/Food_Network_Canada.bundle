VIDEO_URL = 'http://www.foodnetwork.ca/video.html?v='
JSON_URL = 'http://feeds.theplatform.com/ps/JSON/PortalService/2.2/'
FOODNETWORK_PARAMS = ['6yC6lGVHaVA8oWSm1F9PaIYc9tOTzDqY', 'z/FOODNVC%20-%20New%20Video%20Centre']
JSON_CATEGORY_PARAMS = 'getCategoryList?field=ID&field=depth&field=hasReleases&field=fullTitle&PID={0}&query=CustomText|PlayerTag|{1}&field=title&field=fullTitle'
JSON_RELEASE_PARAMS = 'getReleaseList?field=ID&field=contentID&field=PID&field=URL&field=categoryIDs&field=length&field=airdate&field=requestCount&PID={0}&contentCustomField=Show&contentCustomField=Episode&contentCustomField=Network&contentCustomField=Season&contentCustomField=Zone&contentCustomField=Subject&query=Categories|{1}&param=Site|shaw.foodnetwork.ca&query=CategoryIDs|{2}&field=thumbnailURL&field=title&field=length&field=description&field=assets&contentCustomField=Part&contentCustomField=Clip%20Type&contentCustomField=Web%20Exclusive&contentCustomField=ChapterStartTimes&contentCustomField=AlternateHeading&sortField=airdate&sortDescending=true'
JSON_CATEGORY_FEED = JSON_URL + JSON_CATEGORY_PARAMS
ART = 'art-default.jpg'
ICON = 'icon-default.png'
DEFAULT_VIDEO_ICON = ICON

from collections import defaultdict


####################################################################################################
#Utility functions & variables

def emptyList(): return []

def cleanChildren():
    '''
    Weeds out from the children dict all the garbage data i.e the category with no sub category 
    and no releases
    '''
    removeCandidates = []
    for id, value in catInfo.iteritems():
        hasReleases = value[1]
        if len(children[id]) == 0 and not hasReleases:
            removeCandidates.append(id)
    for keys in children.keys():
        children[keys] = [ x for x in children[keys] if x not in removeCandidates]
        

#I don't like having global variables but I can't pass them as parameters of a callback function
catInfo = {}
children = defaultdict(emptyList)
####################################################################################################

####################################################################################################
def Start():
    Plugin.AddPrefixHandler('/video/foodnetwork_ca', CategoryFinder, 'Food Network Canada', ICON, ART)
    ObjectContainer.title1 = 'Food Network Canada'
    ObjectContainer.art = R(ART)
    DirectoryObject.thumb = R(ICON)


####################################################################################################

####################################################################################################
@route('/video/foodnetwork_ca/CategoryFinder')
def CategoryFinder():
    '''
    Parse the JSON file to find all the available categories
    '''
    network = FOODNETWORK_PARAMS
    oc = ObjectContainer()
    jsonData = JSON.ObjectFromURL(JSON_CATEGORY_FEED.format(network[0], network[1]))
    root = []
    children.clear()
    catInfo.clear()
    fullTitleMap = defaultdict(emptyList)
    
    for item in jsonData['items']:
        fullTitle = item['fullTitle']        
        title = item['title']
        id = item['ID']
        hasReleases = item['hasReleases']
        depth = item['depth']
        
        fullTitleMap[fullTitle] = id
        catInfo[id] = title, hasReleases
        if depth > 0:
            parentIdx = fullTitle.rfind(title)
            #We want the parent full title without the trailing /
            parentId = fullTitleMap[fullTitle[:parentIdx-1]]
            children[parentId].append(id)
        else:
            root.append(id)
    cleanChildren()
    #Remove FOODNVC from the list and add the children instead to mimic the category structure 
    #of the website
    root.remove(2304116546)
    root = root + children[2304116546]
    
    for catId in root:
        cat, hasReleases = catInfo[catId]
        if len(children[catId]) > 0 or hasReleases:
            oc.add(DirectoryObject(
                            key = Callback(addSubCategory, parentId=catId, 
                                pid=network[0], site=network[1]),
                            title = cat))
    return oc


@route('/video/foodnetwork_ca/addSubCategory')
def addSubCategory(parentId, pid, site):
    parentId = int(parentId)
    parentTitle, hasReleases = catInfo[parentId]
    oc = ObjectContainer(title2 = parentTitle)
    
    if hasReleases:
        jsonData = JSON.ObjectFromURL(JSON_URL + JSON_RELEASE_PARAMS.format(pid, site, parentId))
        for item in jsonData['items']:
            thumb = item['thumbnailURL']
            videoName = item['title']
            description = item['description']
            id = item['contentID']
            video_url = VIDEO_URL + str(id)
            oc.add(VideoClipObject(url=video_url, title=videoName, summary=description,
                thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=DEFAULT_VIDEO_ICON)))
                
    for subCatId in children[parentId]:
        subCatTitle, hasReleases = catInfo[subCatId]
        if len(children[subCatId]) > 0 or hasReleases:
            oc.add(DirectoryObject(
                        key = Callback(addSubCategory, parentId=subCatId, pid=pid, site=site),
                        title = subCatTitle))
            
    return oc