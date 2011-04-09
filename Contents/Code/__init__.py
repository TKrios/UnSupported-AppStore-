#import os
#import plugin_details.json as plugins
#from Framework.api.helperkit import Popen
#from subprocess import *
#import subprocess as SUBPROCESS

APPLICATIONS_PREFIX = "/applications/unsupportedappstore"

NAME = L('Title')

ART         = 'art-default.jpg'
ICON        = 'icon-default.png'
PREFS_ICON  = 'prefs-icon.png'

PLUGINS     = 'plugin_details.json'

PLEXPATH          = '/Library/Application Support/Plex Media Server/Plug-ins'
#GITPATH             = '/usr/bin'
#GITPATHCHECK        = '/usr/local/git/bin'
#GITPATHCHECKMACPORT = '/opt/local/bin/git'
#PATH=${GITPATH}:${PATH}



####################################################################################################

def Start():

    Plugin.AddPrefixHandler(APPLICATIONS_PREFIX, ApplicationsMainMenu, NAME, ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    
    MediaContainer.title1 = NAME
    MediaContainer.viewGroup = "List"
    MediaContainer.art = R(ART)
    
    HTTP.CacheTime = CACHE_1HOUR
    
def ValidatePrefs():
    #u = Prefs['username']
    #p = Prefs['password']
    #if( u and p ):
    #    return MessageContainer("Success", "User and password provided ok")
    #else:
    #    return MessageContainer("Error", "You need to provide both a user and password")
    return
 

def ApplicationsMainMenu():
    
    if Dict['installed'] == None:
        Dict['installed'] = {}
    if not GitCheck():
        return MessageContainer(NAME, 'git not found! please make sure git is installed and git PATH for non-terminal apps is setup.')
    dir = MediaContainer(viewGroup="InfoList")
    Dict['plugins'] = LoadData()
    for plugin in Dict['plugins']:
        if Installed(plugin):
            subtitle = 'Installed'
        else:
            subtitle = ''
        dir.Append(Function(PopupDirectoryItem(PluginMenu, title=plugin['title'], subtitle=subtitle, summary=plugin['description'], thumb=R(plugin['icon'])), plugin=plugin))
    
    dir.Append(Function(DirectoryItem(UpdateAll, "Download updates", "Update all installed plugins", "This may take a while and will require you to restart PMS for changes to take effect",
        thumb=R(ICON))))
    dir.Append(PrefsItem(title="Your preferences",subtile="So you can set preferences",summary="lets you set preferences",thumb=R(ICON)))

    return dir

def GitCheck():
    try:
        if Dict['GitPath']:
            return True
        else:
            pass
    except:
        gitpath = Helper.Run('which_git.sh')
        if gitpath == '':
            Log('git path not found, please install git and ensure that the PATH is setup for non-terminal programs')
            return False
        else:
            Log('git path: %s' % gitpath)
        Dict['GitPath'] = gitpath
    return True

def PluginMenu(sender, plugin):
    dir = MediaContainer(title1=sender.itemTitle)
    if Installed(plugin):
        #dir.Append(Function(DirectoryItem(UpdatePlugin, title='Update'), plugin=plugin))
        dir.Append(Function(DirectoryItem(UnInstallPlugin, title='UnInstall'), plugin=plugin))
    else:
        dir.Append(Function(DirectoryItem(InstallPlugin, title='Install'), plugin=plugin))
    return dir
  
def LoadData():
    userdata = Resource.Load(PLUGINS)
    Log('Loaded userdata: %s' % userdata)
    return JSON.ObjectFromString(userdata)

def Installed(plugin):
    try:
        if Dict['installed'][plugin['title']] == True:
            Log('registered as installed')
            return True
        else:
            Log('no record of installation found')
            pass
    except:
        pass
    if Helper.Run('exists.sh', '%s/%s' % (PLEXPATH, plugin['bundle'])):
        title = plugin['title']
        Dict['installed'][title] = True
        return True
    
    return False

def InstallPlugin(sender, plugin):
    install = Helper.Run('git_clone.sh', '%s/%s' % (PLEXPATH, plugin['bundle']), plugin['repo'])
    Log(install)
    Dict['installed'][plugin['title']] = True
    return MessageContainer(NAME, '%s installed, restart PMS for changes to take effect.' % sender.itemTitle)
    
def UpdatePlugin(plugin):
    update = Helper.Run('git_pull.sh', '%s/%s' % (PLEXPATH, plugin['bundle']), plugin['repo'])
    Log(update)
    return

def UpdateAll(sender):
    for plugin in Dict['plugins']:
        try:
            if Dict['installed'][plugin['title']] == True:
                Log('%s is installed. Downloading updates' % plugin['title'])
                update = UpdatePlugin(plugin)
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
    Dict['installed'][plugin['title']] = False
    return MessageContainer(NAME, '%s uninstalled. Restart PMS for changes to take effect.' % plugin['title'])