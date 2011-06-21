import os, zipfile
import urlgrabber

####################################################################################################

APPLICATIONS_PREFIX = "/applications/unsupportedappstore"

NAME = L('Title')

ART         = 'art-default.jpg'
ICON        = 'icon-default.png'
PREFS_ICON  = 'icon-prefs.png'

PLUGINS     = 'plugin_details.json'

DEVMODE     = True

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
        
    Log('Plex support files are at ' + Core.app_support_path)
    Log('Plug-in bundles are located in ' + Core.config.bundles_dir_name)
    
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
    dir.Append(Function(DirectoryItem(NewMenu, 'New', thumb = R(ICON))))
    dir.Append(Function(DirectoryItem(AllMenu, 'All', thumb = R(ICON))))
    if Prefs['adult']:
        dir.Append(Function(DirectoryItem(GenreMenu, 'Adult', thumb=R(ICON))))
    dir.Append(Function(DirectoryItem(GenreMenu, 'Application', thumb=R(ICON))))
    dir.Append(Function(DirectoryItem(GenreMenu, 'Video', thumb=R(ICON))))
    dir.Append(Function(DirectoryItem(GenreMenu, 'Pictures', thumb=R(ICON))))
    dir.Append(Function(DirectoryItem(GenreMenu, 'Metadata Agent', thumb=R(ICON))))
    dir.Append(Function(DirectoryItem(GenreMenu, 'Music', thumb=R(ICON))))
    dir.Append(Function(DirectoryItem(InstalledMenu, 'Installed', thumb=R(ICON))))
    dir.Append(Function(DirectoryItem(UpdateAll, "Download updates", "Update all installed plugins", "This may take a while and will require you to restart PMS for changes to take effect",
        thumb=R(ICON))))
    dir.Append(PrefsItem(title="Preferences", thumb=R(PREFS_ICON)))

    return dir

def GenreMenu(sender):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup='InfoList', noCache=True)
    genre = sender.itemTitle
    plugins = Dict['plugins']
    plugins.sort()
    for plugin in plugins:
        if plugin['title'] != "UnSupported Appstore":
            if not Prefs['adult']:
                if "Adult" in plugin['type']:
                    continue
                else:
                    pass
            else:
                pass
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
    plugins = Dict['plugins']
    plugins.sort()
    for plugin in plugins:
        if plugin['title'] != "UnSupported Appstore":
            if not Prefs['adult']:
                if "Adult" in plugin['type']:
                    continue
                else:
                    pass
            else:
                pass
            if Installed(plugin):
                if Dict['Installed'][plugin['title']]['updateAvailable'] == "True":
                    subtitle = 'Update available'
                else:
                    subtitle = 'Installed'
            else:
                subtitle = ''
            dir.Append(Function(PopupDirectoryItem(PluginMenu, title=plugin['title'], subtitle=subtitle, summary=plugin['description'], thumb=R(plugin['icon'])), plugin=plugin))
    return dir

def NewMenu(sender):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup='InfoList', noCache=True)
    plugins = Dict['plugins']
    plugins.reverse()
    for plugin in plugins:
        if plugin['title'] != "UnSupported Appstore":
            if not Prefs['adult']:
                if "Adult" in plugin['type']:
                    continue
                else:
                    pass
            else:
                pass
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
    plugins = Dict['plugins']
    plugins.sort()
    for plugin in plugins:
        subtitle = ''
        if Installed(plugin):
            if Dict['Installed'][plugin['title']]['updateAvailable'] == "True":
                subtitle = 'Update available'
            dir.Append(Function(PopupDirectoryItem(PluginMenu, title=plugin['title'], subtitle=subtitle, summary=plugin['description'], thumb=R(plugin['icon'])), plugin=plugin))
    #dir.Sort()
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
    except:
        Dict['Installed'][plugin['title']] = {"installed":"False", "lastUpdate":"None", "updateAvailable":"True"}
        return False
    
    return False

def InstallPlugin(sender, plugin):
    if Installed(plugin):
        update = Install(plugin)
        Log(update)
    else:
        install = Install(plugin)
        Log(install)
    return MessageContainer(NAME, '%s installed, restart PMS for changes to take effect.' % sender.itemTitle)
    
def Install(plugin):
    bundlePath = '%s/%s' % (GetPluginDirPath, plugin['bundle'])
    Log('bundlePath = ' + bundlePath)
    zipPath = 'http://nodeload.%s/zipball/%s' % (plugin['repo'].split('@')[1].replace(':','/')[:-4], plugin['branch'])
    Log('zipPath = ' + zipPath)
    install = Helper.Run('download_install.sh', GetPlexPath(), plugin['bundle'], zipPath)
    #zipBundle = download???
    #zipBundle.extractall(bundlePath)
    Dict['Installed'][plugin['title']]['installed'] = "True"
    Log('%s "Installed" set to: %s' % (plugin['title'], Dict['Installed'][plugin['title']]['installed']))
    Dict['Installed'][plugin['title']]['lastUpdate'] = Datetime.Now()
    Log('%s "LastUpdate" set to: %s' % (plugin['title'], Dict['Installed'][plugin['title']]['lastUpdate']))
    Dict['Installed'][plugin['title']]['updateAvailable'] = "False"
    Log('%s "updateAvailable" set to: %s' % (plugin['title'], Dict['Installed'][plugin['title']]['updateAvailable']))
    return install

def UpdateAll(sender):
    for plugin in Dict['plugins']:
        if DEVMODE:
            if plugin['title'] == "UnSupported Appstore":
                continue
            else:
                pass
        else:
            pass
        if Dict['Installed'][plugin['title']]['installed'] == "True":
            if Dict['Installed'][plugin['title']]['updateAvailable'] == "False":
                Log('%s is already up to date.' % plugin['title'])
            else:
                Log('%s is installed. Downloading updates:' % (plugin['title']))
                update = Install(plugin)
                Log(update)
        else:
            Log('%s is not installed.' % plugin['title'])
            pass

    return MessageContainer(NAME, 'Updates have been applied. Restart PMS for changes to take effect.')
    
def UnInstallPlugin(sender, plugin):
    file = ('%s/%s' % (GetPluginDirPath(), plugin['bundle']))
    os.remove(file)
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
                    elif mostRecent > Dict['Installed'][plugin['title']]['lastUpdate']:
                        Dict['Installed'][plugin['title']]['updateAvailable'] = "True"
                    else:
                        Dict['Installed'][plugin['title']]['updateAvailable'] = "False"
                    
                    if Dict['Installed'][plugin['title']]['updateAvailable'] == "True":
                        Log('Update available')
                    else:
                        Log('Up-to-date')
    return

def GetPlexPath():
    return Core.app_support_path
    
def GetPluginDirPath():
    return '%s/%s' % (Core.app_support_path, Core.config.bundles_dir_name)