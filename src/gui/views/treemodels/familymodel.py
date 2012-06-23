#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Nick Hall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".")
import locale

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Utils
import gen.datehandler
from gen.display.name import displayer as name_displayer
import gen.lib
from gen.lib import EventRoleType
from gui.views.treemodels.flatbasemodel import FlatBaseModel
from gen.config import config

invalid_date_format = config.get('preferences.invalid-date-format')

#-------------------------------------------------------------------------
#
# FamilyModel
#
#-------------------------------------------------------------------------
class FamilyModel(FlatBaseModel):

    def __init__(self, db, scol=0, order=gtk.SORT_ASCENDING, search=None, 
                 skip=set(), sort_map=None):
        self.gen_cursor = db.get_family_cursor
        self.map = db.get_raw_family_data
        self.fmap = [
            self.column_id, 
            self.column_father, 
            self.column_mother, 
            self.column_type, 
            self.column_marriage, 
            self.column_tags,
            self.column_change, 
            self.column_handle, 
            self.column_tag_color,
            self.column_tooltip,
            ]
        self.smap = [
            self.column_id, 
            self.sort_father, 
            self.sort_mother, 
            self.column_type, 
            self.sort_marriage, 
            self.column_tags,
            self.sort_change, 
            self.column_handle, 
            self.column_tag_color,
            self.column_tooltip,
            ]
        FlatBaseModel.__init__(self, db, scol, order, tooltip_column=9, 
                           search=search, skip=skip, sort_map=sort_map)

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        self.db = None
        self.gen_cursor = None
        self.map = None
        self.fmap = None
        self.smap = None
        FlatBaseModel.destroy(self)

    def color_column(self):
        """
        Return the color column.
        """
        return 8

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_handle(self, data):
        return unicode(data[0])

    def column_father(self, data):
        if data[2]:
            person = self.db.get_person_from_handle(data[2])
            return unicode(name_displayer.sorted_name(person.primary_name))
        else:
            return u""

    def sort_father(self, data):
        if data[2]:
            person = self.db.get_person_from_handle(data[2])
            return name_displayer.sort_string(person.primary_name)
        else:
            return u""

    def column_mother(self, data):
        if data[3]:
            person = self.db.get_person_from_handle(data[3])
            return unicode(name_displayer.sorted_name(person.primary_name))
        else:
            return u""

    def sort_mother(self, data):
        if data[3]:
            person = self.db.get_person_from_handle(data[3])
            return name_displayer.sort_string(person.primary_name)
        else:
            return u""

    def column_type(self, data):
        return unicode(gen.lib.FamilyRelType(data[5]))

    def column_marriage(self, data):
        from gen.utils import get_marriage_or_fallback
        family = self.db.get_family_from_handle(data[0])
        event = get_marriage_or_fallback(self.db, family, "<i>%s</i>")
        if event:
            if event.date.format:
                return event.date.format % gen.datehandler.displayer.display(event.date)
            elif not gen.datehandler.get_date_valid(event):
                return invalid_date_format % gen.datehandler.displayer.display(event.date)
            else:
                return "%s" % gen.datehandler.displayer.display(event.date)
        else:
            return u''

    def sort_marriage(self, data):
        from gen.utils import get_marriage_or_fallback
        family = self.db.get_family_from_handle(data[0])
        event = get_marriage_or_fallback(self.db, family)
        if event:
            return "%09d" % event.date.get_sort_value()
        else:
            return u''

    def column_id(self, data):
        return unicode(data[1])

    def sort_change(self, data):
        return "%012x" % data[12]
    
    def column_change(self, data):
        return gen.datehandler.format_time(data[12])

    def column_tooltip(self, data):
        return u'Family tooltip'

    def get_tag_name(self, tag_handle):
        """
        Return the tag name from the given tag handle.
        """
        return self.db.get_tag_from_handle(tag_handle).get_name()
        
    def column_tag_color(self, data):
        """
        Return the tag color.
        """
        tag_color = None
        tag_priority = None
        for handle in data[13]:
            tag = self.db.get_tag_from_handle(handle)
            this_priority = tag.get_priority()
            if tag_priority is None or this_priority < tag_priority:
                tag_color = tag.get_color()
                tag_priority = this_priority
        return tag_color

    def column_tags(self, data):
        """
        Return the sorted list of tags.
        """
        tag_list = map(self.get_tag_name, data[13])
        return ', '.join(sorted(tag_list, key=locale.strxfrm))
