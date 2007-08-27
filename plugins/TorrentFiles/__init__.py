# Copyright (C) 2007
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA.

### Initialization ###

plugin_name = _("Torrent Files")
plugin_author = "Deluge"
plugin_version = "0.2"
plugin_description = _("""
This plugin shows you the files inside a torrent and allows you to set \
priorities for them and choose which ones you want or don't want to download.
""")

def deluge_init(deluge_path):
    global path
    path = deluge_path

def enable(core, interface):
    global path
    return TorrentFiles(path, core, interface)

### The Plugin ###
import gtk

import deluge
from TorrentFiles.tab_files import FilesTabManager

class TorrentFiles:
    def __init__(self, path, core, interface):
        print "Loading TorrentFiles plugin..."
        self.parent = interface
        self.manager = core
        config_file = deluge.common.CONFIG_DIR + "/files.conf"
        self.config = deluge.pref.Preferences(config_file, False, 
                          defaults={'file_viewer': 'xdg-open'})
        try:
            self.config.load()
        except IOError:
            # File does not exist
            pass

        self.glade = gtk.glade.XML(path + "/files_preferences.glade")
        self.dialog = self.glade.get_widget("dialog")
        self.glade.signal_autoconnect({
                                        'on_button_cancel_clicked': self.on_button_cancel_clicked,
                                        'on_button_ok_clicked': self.on_button_ok_clicked
                                      })

        tree_view = gtk.TreeView()
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.add(tree_view)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.top_widget = scrolled_window

        self.parent_notebook = self.parent.notebook
        self.parent_notebook.append_page(scrolled_window, 
                                         gtk.Label(_("Files")))
        
        tree_view.show()
        scrolled_window.show()
        
        self.tab_files = FilesTabManager(tree_view, core)
        self.tab_files.build_file_view()
        self.tab_files.set_file_viewer(self.config.get("file_viewer"))

    def unload(self):
        self.tab_files.clear_file_store()
        tab_page = self.parent_notebook.page_num(self.top_widget)
        self.parent_notebook.remove_page(tab_page)
        self.config.save()

    def update(self):
        if not self.parent.update_interface:
            return

        tab_page = self.parent_notebook.page_num(self.top_widget)
        current_page = self.parent_notebook.get_current_page()
        
        if tab_page == current_page:
            unique_id = self.parent.get_selected_torrent()
            
            if unique_id is None or \
               unique_id in self.manager.removed_unique_ids:
                # If no torrents added or more than one torrent selected
                self.tab_files.clear_file_store()
                self.tab_files.set_unique_id(None)
                return
            
            if self.tab_files.file_unique_id != unique_id:
                self.tab_files.clear_file_store()
                self.tab_files.set_unique_id(unique_id)
                self.tab_files.prepare_file_store()
            else:
                self.tab_files.update_file_store()
                
    def configure(self, window):
        self.glade.get_widget("file_viewer").\
            set_text(self.config.get("file_viewer"))
        self.dialog.set_transient_for(window)
        self.dialog.show()

    def on_button_ok_clicked(self, button):
        self.dialog.hide()
        
        self.config.set("file_viewer", 
                        self.glade.get_widget("file_viewer").get_text())
        self.config.save()
        
        self.tab_files.set_file_viewer(self.config.get("file_viewer"))
    
    def on_button_cancel_clicked(self, button):
        self.dialog.hide()
