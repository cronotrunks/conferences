#!/usr/bin/env python

# This program displays a "pulsing" (or whatever it's called)
# ProgressBar, adds a timeout function to keep it updated, and shows
# how to obtain an individual widget that libglade created.
#
# Note that most programs update progress bars during some kind of
# function that doesn't return to the main event loop (unlike this
# simple example).  In that case, you must manually tell gtk to update
# widgets yourself by calling gtk.events_pending() and
# gtk.main_iteration().  (See example-3.py for an example of doing
# this in a different context).

import gtk
import gtk.glade
import time
import gobject

class WasteTimeWindow:
  def __init__(self, glade_file):
    # Parse the glade file
    self.what_a_waste = gtk.glade.XML(glade_file)

    # Get the progress bar widget and change it to "activity mode",
    # i.e. a block that bounces back and forth instead of a normal
    # progress bar that fills to completion.
    self.progress_bar = self.what_a_waste.get_widget("Progress Bar")
    self.progress_bar.pulse()

    # Add a timeout to update the progress bar every 100 milliseconds or so
    self.timeout_handler_id = gobject.timeout_add(1000, self.update_progress_bar)

    # Start a timer to see how long the user runs this program
    self.start = time.time()

    # Connect signals specified in the .glade file
    self.what_a_waste.signal_autoconnect(
      {"inform_user_of_time_wasted" : self.inform_user_of_time_wasted })

  # This is the callback for the delete_event, i.e. window closing
  def inform_user_of_time_wasted(self, window, event):
    # Tell the user how much time they used
    print 'You wasted %.2f seconds with this program' % (time.time()-self.start)

    # Remove the timer so that gtk doesn't try to keep updating the progress
    # bar
    gobject.source_remove(self.timeout_handler_id)

    # Make the main event loop quit
    gtk.main_quit()

    # No other handlers need be called...
    return False

  def update_progress_bar(self):
    self.progress_bar.pulse()

    # Return true so the function will be called again; returning
    # false removes this timeout function.
    return True

# Create the WasteTimeWindow
window = WasteTimeWindow("progressbar.glade")

# start the event loop
gtk.main()
