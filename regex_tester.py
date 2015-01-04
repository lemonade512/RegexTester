#!/usr/bin/env python

import gtk
import pango
import re


class RegexApp(gtk.Window):

    def __init__(self, *args, **kwargs):
        """ Initializes the GUI elements and sets the regex to None. """
        super(RegexApp, self).__init__(*args, **kwargs)

        self.set_size_request(500, 500)
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("destroy", gtk.main_quit)

        main_vbox = gtk.VBox()

        entry = gtk.Entry()
        entry.connect("changed", self.entry_changed)
        main_vbox.pack_start(entry, False, False)

        main_hbox = gtk.HBox()

        scroll = gtk.ScrolledWindow()
        self.textview = gtk.TextView()
        buf = self.textview.get_buffer()
        buf.set_text("ACG ACT\nACT\nAGA\nCGA\nCTA\nCGT")
        buf.connect("changed", self.match_regex)
        self.red_tag = buf.create_tag("fg_red", foreground='red',
                                            underline=pango.UNDERLINE_SINGLE)
        self.blue_tag = buf.create_tag("fg_blue", foreground='blue',
                                            underline=pango.UNDERLINE_SINGLE)
        self.green_tag = buf.create_tag("fg_green", foreground='green',
                                            underline=pango.UNDERLINE_SINGLE)
        scroll.add(self.textview)
        main_hbox.pack_start(scroll)

        flags_eb = gtk.EventBox()
        flags_vbox = gtk.VBox()
        flags_vbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))

        ignore_case_flag = gtk.CheckButton("Ignore Case")
        ignore_case_flag.connect("toggled", self.flag_activated, re.IGNORECASE)
        flags_vbox.pack_start(ignore_case_flag, False, False)

        multiline_flag = gtk.CheckButton("Multiline")
        multiline_flag.connect("toggled", self.flag_activated, re.MULTILINE)
        flags_vbox.pack_start(multiline_flag, False, False)
        flags_eb.add(flags_vbox)
        #flags_eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))

        main_hbox.pack_start(flags_eb, False, False)

        main_vbox.pack_start(main_hbox)
        self.add(main_vbox)
        self.show_all()

        self.regex = None
        # An integer value that represents the state of all the flags
        self.flags = 0

    def flag_activated(self, btn, flag):
        print "Activated", btn.get_label(), btn.get_active()
        if btn.get_active():
            self.flags |= flag
        else:
            self.flags &= ~flag
        self.match_regex()

    def entry_changed(self, entry):
        """ Called when the regex entry has changed.

        This function sets the new regex in the Entry if it is properly
        formatted and then matches the regex in the text view.
        """
        self._set_regex(entry.get_text())
        self.match_regex()

    def _set_regex(self, regex):
        """ If regex is properly formatted self.regex is set. """
        try:
            re.compile(regex)
            self.regex = regex
        except re.error, e:
            print e

    def match_regex(self, *args):
        """ Updates the textview to show the text matched by the regex. """
        if self.regex:
            buf = self.textview.get_buffer()
            buf.remove_all_tags(buf.get_start_iter(), buf.get_end_iter())
            text = buf.get_text(buf.get_start_iter(), buf.get_end_iter())
            for i,line in enumerate(text.split('\n')):
                m = re.search(self.regex, line, flags=self.flags)
                if m:
                    start = buf.get_iter_at_line_offset(i, m.span()[0])
                    end = buf.get_iter_at_line_offset(i, m.span()[1])
                    buf.apply_tag(self.red_tag, start, end)
                    for group_num, g in enumerate(m.groups()):
                        if m.start(group_num+1) == -1:
                            #TODO is this case handled properly? (seems to work but not
                            #sure if I should do anything else here).
                            continue
                        start = buf.get_iter_at_line_offset(i, m.start(group_num+1))
                        end = buf.get_iter_at_line_offset(i, m.end(group_num+1))
                        print g, m.start(group_num+1), m.end(group_num+1)
                        buf.apply_tag(self.green_tag, start, end)


if __name__ == "__main__":
    app = RegexApp()
    gtk.main()
