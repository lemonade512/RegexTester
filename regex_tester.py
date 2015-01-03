#!/usr/bin/env python

import gtk
import pango
import re


class RegexApp(gtk.Window):

    def __init__(self, *args, **kwargs):
        super(RegexApp, self).__init__(*args, **kwargs)

        self.set_size_request(500, 500)
        self.connect("destroy", gtk.main_quit)

        main_vbox = gtk.VBox()

        entry = gtk.Entry()
        entry.connect("changed", self.entry_changed)
        main_vbox.pack_start(entry, False, False)

        scroll = gtk.ScrolledWindow()
        self.textview = gtk.TextView()
        buf = self.textview.get_buffer()
        buf.set_text("ACG ACT\nACT\nAGA\nCGA\nCTA\nCGT")
        buf.connect("changed", self.match_regex)
        self.red_tag = buf.create_tag("fg_red", foreground='red',
                                            underline=pango.UNDERLINE_SINGLE)
        self.blue_tag = buf.create_tag("fg_blue", foreground='blue',
                                            underline=pango.UNDERLINE_SINGLE)
        scroll.add(self.textview)
        main_vbox.pack_start(scroll)

        self.add(main_vbox)
        self.show_all()

        self.regex = None

    def entry_changed(self, entry):
        try:
            self.regex = re.compile(entry.get_text())
            self.match_regex()
        except re.error, e:
            print e

    def match_regex(self, *args):
        if self.regex:
            buf = self.textview.get_buffer()
            buf.remove_all_tags(buf.get_start_iter(), buf.get_end_iter())
            text = buf.get_text(buf.get_start_iter(), buf.get_end_iter())
            for i,line in enumerate(text.split('\n')):
                m = self.regex.search(line)
                if m:
                    start = buf.get_iter_at_line_offset(i, m.span()[0])
                    end = buf.get_iter_at_line_offset(i, m.span()[1])
                    buf.apply_tag(self.red_tag, start, end)
                    for group_num, g in enumerate(m.groups()):
                        start = buf.get_iter_at_line_offset(i, m.start(group_num+1))
                        end = buf.get_iter_at_line_offset(i, m.end(group_num+1))
                        print g, m.start(group_num+1), m.end(group_num+1)
                        buf.apply_tag(self.blue_tag, start, end)


if __name__ == "__main__":
    app = RegexApp()
    gtk.main()
