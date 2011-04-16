APPLICATIONS_PREFIX = "/applications/unsupportedappstore"

NAME = L('Title')

ART         = 'art-default.jpg'
ICON        = 'icon-default.png'
PREFS_ICON  = 'prefs-icon.png'

PLUGINS     = 'plugin_details.json'

PLEXPATH    = '/Library/Application Support/Plex Media Server/Plug-ins'

####################################################################################################

def Start():

    Plugin.AddPrefixHandler(APPLICATIONS_PREFIX, ApplicationsMainMenu, NAME, ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    
    MediaContainer.title1 = NAME
    MediaContainer.viewGroup = "List"
    MediaContainer.art = R(ART)
    
    HTTP.CacheTime = CACHE_1HOUR
    
    #Check the list of installed plugins
    if Dict['Installed'] == None:
        Dict['Installed'] = {}
    else:
        Log(Dict['Installed'])
    
def ValidatePrefs():
    #u = Prefs['username']
    #p = Prefs['password']
    #if( u and p ):
    #    return MessageContainer("Success", "User and password provided ok")
    #else:
    #    return MessageContainer("Error", "You need to provide both a user and password")
    return
 

def ApplicationsMainMenu():
    
    #Load the list of available plugins
    Dict['plugins'] = LoadData()
    
    #Check for available updates
    updates = CheckForUpdates()
    
    dir = MediaContainer(viewGroup="List", noCache=True)
    dir.Append(Function(DirectoryItem(AllMenu, 'All', thumb = R(ICON))))
    dir.Append(Function(DirectoryItem(GenreMenu, 'Application', thumb=R(ICON))))
    dir.Append(Function(DirectoryItem(GenreMenu, 'Video', thumb=R(ICON))))
    dir.Append(Function(DirectoryItem(GenreMenu, 'Photo', thumb=R(ICON))))
    dir.Append(Function(DirectoryItem(GenreMenu, 'Music', thumb=R(ICON))))
    dir.Append(Function(DirectoryItem(InstalledMenu, 'Installed', thumb=R(ICON))))
    dir.Append(Function(DirectoryItem(UpdateAll, "Download updates", "Update all installed plugins", "This may take a while and will require you to restart PMS for changes to take effect",
        thumb=R(ICON))))
    #dir.Append(PrefsItem(title="Preferences", thumb=R(PREFS_ICON)))

    return dir

def GenreMenu(sender):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup='InfoList', noCache=True)
    genre = sender.itemTitle
    for plugin in Dict['plugins']:
        if plugin['title'] != "UnSupported Appstore":
            if genre in plugin['type']:
                if Installed(plugin):
                    if Dict['Installed'][plugin['title']]['updateAvailable'] == "True":
                        subtitle = 'Update available'
                    else:
                        subtitle = 'Installed'
                else:
                    subtitle = ''
                dir.Append(Function(PopupDirectoryItem(PluginMenu, title=plugin['title'], subtitle=subtitle, summary=plugin['description'], thumb=R(plugin['icon'])), plugin=plugin))
    return dir

def AllMenu(sender):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup='InfoList', noCache=True)
    for plugin in Dict['plugins']:
        if plugin['title'] != "UnSupported Appstore":
            if Installed(plugin):
                if Dict['Installed'][plugin['title']]['updateAvailable'] == "True":
                    subtitle = 'Update available'
                else:
                    subtitle = 'Installed'
            else:
                subtitle = ''
            dir.Append(Function(PopupDirectoryItem(PluginMenu, title=plugin['title'], subtitle=subtitle, summary=plugin['description'], thumb=R(plugin['icon'])), plugin=plugin))
    return dir

def InstalledMenu(sender):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup='InfoList', noCache=True)
    for plugin in Dict['plugins']:
        subtitle = ''
        if Installed(plugin):
            if Dict['Installed'][plugin['title']]['updateAvailable'] == "True":
                subtitle = 'Update available'
            dir.Append(Function(PopupDirectoryItem(PluginMenu, title=plugin['title'], subtitle=subtitle, summary=plugin['description'], thumb=R(plugin['icon'])), plugin=plugin))
    return dir

def PluginMenu(sender, plugin):
    dir = MediaContainer(title1=sender.itemTitle, noCache=True)
    if Installed(plugin):
        if Dict['Installed'][plugin['title']]['updateAvailable'] == "True":
            dir.Append(Function(DirectoryItem(InstallPlugin, title='Update'), plugin=plugin))
        dir.Append(Function(DirectoryItem(UnInstallPlugin, title='UnInstall'), plugin=plugin))
    else:
        dir.Append(Function(DirectoryItem(InstallPlugin, title='Install'), plugin=plugin))
    return dir
  
def LoadData():
    userdata = Resource.Load(PLUGINS)
    return JSON.ObjectFromString(userdata)

def Installed(plugin):
    try:
        if Dict['Installed'][plugin['title']]['installed'] == "True":
            return True
        else:
            return False
            pass
    except:
        if Helper.Run('exists.sh', '%s/%s' % (PLEXPATH, plugin['bundle'])):
            Dict['Installed'][plugin['title']] = {"installed":"True", "lastUpdate":"None", "updateAvailable":"True"}
            return True
    
    return False

def InstallPlugin(sender, plugin):
    if Installed(plugin):
        update = Install(plugin)
    else:
        install = Install(plugin)
    return MessageContainer(NAME, '%s installed, restart PMS for changes to take effect.' % sender.itemTitle)
    
def Install(plugin):
    zipPath = 'http://nodeload.%s/zipball/%s' % (plugin['repo'].split('@')[1].replace(':','/')[:-4], plugin['branch'])
    install = Helper.Run('download_install.sh', PLEXPATH, plugin['bundle'], zipPath)
    Log(install)
    Dict['Installed'][plugin['title']]['lastUpdate'] = Datetime.Now()
    Dict['Installed'][plugin['title']]['updateAvailable'] = "False"
    return

def UpdateAll(sender):
    for plugin in Dict['plugins']:
        try:
            if Dict['Installed'][plugin['title']]['installed'] == "True":
                Log('%s is installed. Downloading updates' % plugin['title'])
                update = Install(plugin)
            else:
                Log('%s is not installed.' % plugin['title'])
                pass
        except:
            Log('%s is not installed.' % plugin['title'])
            pass
        
    return MessageContainer(NAME, 'Updates have been applied. Restart PMS for changes to take effect.')
    
def UnInstallPlugin(sender, plugin):
    uninstall = Helper.Run('remove_plugin.sh', '%s/%s' % (PLEXPATH, plugin['bundle']))
    Log(uninstall)
    Dict['Installed'][plugin['title']]['installed'] = "False"
    return MessageContainer(NAME, '%s uninstalled. Restart PMS for changes to take effect.' % plugin['title'])
    
def CheckForUpdates():
    #use the github commit feed for each installed plugin to check for available updates
    @parallelize
    def GetUpdateList():
        for num in range(len(Dict['plugins'])):
            @task
            def GetRSSFeed(num=num):
                plugin = Dict['plugins'][num]
                if Installed(plugin):
                    rssURL = 'https://%s/commits/master.atom' % plugin['repo'].split('@')[1].replace(':','/')[:-4]
                    #Log(rssURL)
                    commits = HTML.ElementFromURL(rssURL)
                    mostRecent = Datetime.ParseDate(commits.xpath('//entry')[0].xpath('./updated')[0].text[:-6])
                    if Dict['Installed'][plugin['title']]['lastUpdate'] == "None":
                        Dict['Installed'][plugin['title']]['updateAvailable'] = "True"
                    elif mostRecent >> Dict['Installed'][plugin['title']]['lastUpdate']:
                        Dict['Installed'][plugin['title']]['updateAvailable'] = "True"
                    else:
                        Dict['Installed'][plugin['title']]['updateAvailable'] = "False"
    return