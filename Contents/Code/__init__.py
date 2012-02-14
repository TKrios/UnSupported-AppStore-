import os

####################################################################################################

APPLICATIONS_PREFIX = "/applications/unsupportedappstore"

NAME = L('Title')

ART         = 'art-default.jpg'
ICON        = 'icon-default.png'
PREFS_ICON  = 'icon-prefs.png'

PLUGINS     = 'plugin_details.json'

DEVMODE     = False

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
        Dict['Installed'] = {'UnSupported Appstore' : {'lastUpdate': 'None', 'updateAvailable': 'False', 'installed': 'True'}}
    else:
        Log(Dict['Installed'])
        
    Log('Plex support files are at ' + Core.app_support_path)
    Log('Plug-in bundles are located in ' + Core.config.bundles_dir_name)
    
def ValidatePrefs():
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
    for plugin in plugins:
        if plugin['hidden'] == "True": continue ### Don't display plugins which are "hidden"
        else: pass
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
    for plugin in plugins:
        if plugin['hidden'] == "True": continue ### Don't display plugins which are "hidden"
        else: pass
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
    #Log(plugins)
    try:
        for plugin in plugins:
            plugin['date added'] = Datetime.TimestampFromDatetime(Datetime.ParseDate(plugin['date added']))
    except:
        Log.Exception("Converting dates to timestamps failed")
    #Log(plugins)
    date_sorted = sorted(plugins, key=lambda k: k['date added'])
    Log(date_sorted)
    date_sorted.reverse()
    for plugin in date_sorted:
        if plugin['hidden'] == "True": continue ### Don't display plugins which are "hidden"
        else: pass
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
            if plugin['hidden'] == "True":
                subtitle = 'Now available through the Plex Channel Directory'
            elif Dict['Installed'][plugin['title']]['updateAvailable'] == "True":
                subtitle = 'Update available'
            else: pass
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
        ### make sure the Appstore shows up in the list if it doesn't already ###
        if plugin['title'] == 'UnSupported Appstore':
            Dict['Installed'][plugin['title']] = {"installed":"True", "lastUpdate":"None", "updateAvailable":"False"}
            Dict.Save()
        else:
            Dict['Installed'][plugin['title']] = {"installed":"False", "lastUpdate":"None", "updateAvailable":"True"}
            Dict.Save()
        return False
    
    return False

def InstallPlugin(sender, plugin):
    if Installed(plugin):
        Install(plugin)
    else:
        Install(plugin)
    return MessageContainer(NAME, '%s installed, restart PMS for changes to take effect.' % sender.itemTitle)
    
def Install(plugin):
    zipPath = 'http://nodeload.%s/zipball/%s' % (plugin['repo'].split('@')[1].replace(':','/')[:-4], plugin['branch'])
    Log('zipPath = ' + zipPath)
    #install = Helper.Run('download_install.sh', GetPlexPath(), plugin['bundle'], zipPath)
    Log('Downloading from ' + zipPath)
    zipfile = Archive.ZipFromURL(zipPath)
    #zipBundle = zipfile.ZipFile(urlgrabber.urlgrab(zipPath))
    Log('Extracting to ' + GetBundlePath(plugin))
    
    for filename in zipfile:
        data = zipfile[filename]
        if not str(filename).endswith('/'):
            if not str(filename.split('/')[-1]).startswith('.'):
                filename = ('/').join(filename.split('/')[1:])
                file_path = Core.storage.join_path(GetBundlePath(plugin), *filename.split('/'))
                Log('Extracting file' + file_path)
                Core.storage.save(file_path, data)
            else:
                Log('Skipping "hidden" file: ' + filename)
        else:
            Log(filename.split('/')[-2])
            if not str(filename.split('/')[-2]).startswith('.'):
                filename = ('/').join(filename.split('/')[1:])
                file_path = Core.storage.join_path(GetBundlePath(plugin), *filename.split('/'))
                Log('Extracting folder ' + file_path)
                Core.storage.ensure_dirs(file_path)
        
    Dict['Installed'][plugin['title']]['installed'] = "True"
    Log('%s "Installed" set to: %s' % (plugin['title'], Dict['Installed'][plugin['title']]['installed']))
    Dict['Installed'][plugin['title']]['lastUpdate'] = Datetime.Now()
    Log('%s "LastUpdate" set to: %s' % (plugin['title'], Dict['Installed'][plugin['title']]['lastUpdate']))
    Dict['Installed'][plugin['title']]['updateAvailable'] = "False"
    Log('%s "updateAvailable" set to: %s' % (plugin['title'], Dict['Installed'][plugin['title']]['updateAvailable']))
    Dict.Save()
    return

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
    Log('Uninstalling %s' % GetBundlePath(plugin))
    DeleteFolder(GetBundlePath(plugin))
    Dict['Installed'][plugin['title']]['installed'] = "False"
    Dict.Save()
    return MessageContainer(NAME, '%s uninstalled. Restart PMS for changes to take effect.' % plugin['title'])

def DeleteFile(filePath):
    Log('Removing ' + filePath)
    os.remove(filePath)
    return

def DeleteFolder(folderPath):
    for file in os.listdir(folderPath):
        path = Core.storage.join_path(folderPath, file)
        try:
            DeleteFile(path)
        except:
            DeleteFolder(path)
    Log('Removing ' + folderPath)
    os.rmdir(folderPath)
    return
    
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
                        Log(plugin['title'] + ': Update available')
                    else:
                        Log(plugin['title'] + ': Up-to-date')
        Dict.Save()
    return
    
def GetPluginDirPath():
    return Core.storage.join_path(Core.app_support_path, Core.config.bundles_dir_name)
    
def GetBundlePath(plugin):
    return Core.storage.join_path(GetPluginDirPath(), plugin['bundle'])