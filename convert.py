#!/opt/local/bin/python2

import sys

from appscript import k, app

things = app('Things')
thl = app("The Hit List")

def wipeTHL(thl):
    '''Wipes your THL database. Useful only for testing.'''
    for folder in [thl.inbox]:
        for task in folder.tasks.get():
            task.delete()
            
    for folder in thl.folders_group.folders.get():
        #print item
        folder.delete()

def copyFolder(thingsFolder, thlFolder, trashIds):
    '''Copy the tasks from a Things folder to a THL folder.'''
    for it in thingsFolder.to_dos.get():
        if it.id() in trashIds:
            continue

        ot = thl.make(new=k.task, at=thlFolder)
        # TODO: use getattr and setattr to define a simple from-to field mapping

        ot.title.set(it.name())
        ot.notes.set(it.notes())

        # TODO might need to reformat [url] tags in Things output
        if it.activation_date() != k.missing_value:
            ot.start_date.set(it.activation_date())
        if it.due_date() != k.missing_value:
            ot.due_date.set(it.due_date())
        '''
        if it.cancellation_date() != k.missing_value: # ro
            print "\t\tset due date"
            ot.canceled_date.set(it.cancellation_date())
        if it.creation_date() != k.missing_value:
            print "\t\tset create date"
            ot.created_date.set(it.creation_date()) # might be ro
        if it.modification_date() != k.missing_value:
            print "\t\tset mod date"
            ot.modified_date.set(it.modification_date()) # might be ro
        if it.completion_date() != k.missing_value:
            print "\t\tset completion date"
            ot.completed_date.set(it.completion_date()) # might be ro
        '''
        
        # TODO a way to get better conversion fidelity might be to just modify the sqlite database directly
        # TODO repeating tasks are not preserved!
        
        if it.status() == k.completed:
            ot.completed.set(True)
        elif it.status() == k.canceled:
            ot.canceled.set(True)
        
        print "\t%s" % it.name()

def createTHLList(name):
    f = thl.folders_group.make(new=k.list_)
    f.name.set(name)
    return f

def createTHLFolder(name):
    f = thl.folders_group.make(new=k.folder)
    f.name.set(name)
    return f

def main():
    if '--wipe' in sys.argv:
        print "Wiping your existing THL database..."
        wipeTHL(thl)

    # import the Things Trash folder - tasks are not individually tagged with their Trash status!
    print "Importing Trash..."
    trashIds = set()
    for task in things.lists["Trash"].to_dos.get():
        trashIds.add(task.id())

    createTHLList("Scheduled")

    folderMap = {
        "Inbox": thl.inbox,
        "Today": thl.today_list,
        #"Next": thl., # TODO: maybe make a Smart List in THL for this
        "Scheduled": thl.folders_group.lists["Scheduled"],
        #"Someday": thl.,


        # UNCOMMENT THIS TO PRESERVE LOGBOOK
        # I don't, normally, because conversion is relatively slow and the logbook can be huge.
        "Logbook": thl.inbox, # these will all be archived and so will disappear (but still be recorded)

        #"Trash": thl., # TODO maybe you could go through and figure out which project each item belongs to, then assign it on the dest side and mark it deleted/cancelled/whatever
    }

    print "TODO: not preserving Someday list"
    # For Someday, create a folder and put the individual projects in there, along with a "Tasks" list
    print "TODO: not preserving Trash list"
    # A lot of Trash comes through on the project lists

    for infolder, outfolder in folderMap.items():
        copyFolder(things.lists[infolder], outfolder, trashIds)

    # convert Areas of Responsibility
    # We just create a new list for each. Any projects stored within AoRs are not kept in the hierarchy.
    for src in things.areas.get():
        print src.name()
        dest = createTHLList(src.name())
        copyFolder(src, dest, trashIds)

    for src in things.lists["Projects"].to_dos.get():
        # TODO: transfer the project properties, too (they can be completed, archived, deferred and so on)
        print src.name()
        
        dest = createTHLList(src.name())
        #dest.modified_date.set(project.modification_date()) # TODO readonly
        #dest.created_date.set(project.creation_date()) # TODO readonly
        # TODO 'archived' flag
        #thl.folders_group.help()
        # TODO more attributes
        
        copyFolder(src, dest, trashIds)

    # TODO transfer areas of responsibility - they have both tasks and subprojects
    print
    print "NOTE: not converting logbook folder. It takes a long time. Tweak the source code if you want it!"

    # TODO make a note in the new Today/Inbox reminding the user to do conversion tasks, like manually transferring repeating tasks


if __name__ == '__main__':
    main()
