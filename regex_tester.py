#!/usr/bin/env python

import gtk
import pango
import re
import os


class RegexApp(gtk.Window):

    def __init__(self, *args, **kwargs):
        """ Initializes the GUI elements and sets the regex to None. """
        super(RegexApp, self).__init__(*args, **kwargs)

        # Save files
        home = os.path.expanduser("~")
        self.buf_save_filename = os.path.join(home, ".regex_tester/buffer_save.txt")
        if not os.path.isdir(os.path.dirname(self.buf_save_filename)):
            os.makedirs(os.path.dirname(self.buf_save_filename))

        open(self.buf_save_filename, 'a').close()

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
        f = open(self.buf_save_filename, 'r')
        buf.set_text(f.read())
        f.close()
        buf.connect("changed", self.buffer_changed)
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

        ignore_case_flag = gtk.CheckButton("Ignore Case")
        ignore_case_flag.connect("toggled", self.flag_activated, re.IGNORECASE)
        flags_vbox.pack_start(ignore_case_flag, False, False, padding=5)

        multiline_flag = gtk.CheckButton("Multiline")
        multiline_flag.connect("toggled", self.flag_activated, re.MULTILINE)
        flags_vbox.pack_start(multiline_flag, False, False, padding=5)

        dotall_flag = gtk.CheckButton("Dotall")
        dotall_flag.connect("toggled", self.flag_activated, re.DOTALL)
        flags_vbox.pack_start(dotall_flag, False, False, padding=5)

        flags_eb.add(flags_vbox)
        #flags_eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))

        main_hbox.pack_start(flags_eb, False, False, padding=10)

        main_vbox.pack_start(main_hbox)
        self.add(main_vbox)
        self.show_all()

        self.regex = None
        # An integer value that represents the state of all the flags
        self.flags = 0

    def flag_activated(self, btn, flag):
        """ Called when the user toggles a flag. """
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

    def match_regex(self):
        """ Updates the textview to show the text matched by the regex. """
        if not self.regex:
            self.regex = ""
        buf = self.textview.get_buffer()
        buf.remove_all_tags(buf.get_start_iter(), buf.get_end_iter())
        if not (self.flags & re.MULTILINE):
            self._match_lines(buf)
        else:
            self._match_text(buf)

    def buffer_changed(self, buf):
        f = open(self.buf_save_filename, 'w')
        f.write(buf.get_text(buf.get_start_iter(), buf.get_end_iter()))
        f.close()

        self.match_regex()

    def _set_regex(self, regex):
        """ If regex is properly formatted self.regex is set. """
        try:
            re.compile(regex)
            self.regex = regex
        except re.error, e:
            print e

    #TODO _match_lines and _match_text are very similar. Is there a way to combine
    # the two for less code?
    def _match_lines(self, buf):
        text = buf.get_text(buf.get_start_iter(), buf.get_end_iter())
        for i,line in enumerate(text.split('\n')):
            m = re.search(self.regex, line, flags=self.flags)

            # If there is no match on this line continue to the next
            if not m:
                continue

            start = buf.get_iter_at_line_offset(i, m.span()[0])
            end = buf.get_iter_at_line_offset(i, m.span()[1])
            buf.apply_tag(self.red_tag, start, end)
            for group_num, g in enumerate(m.groups()):
                if m.start(group_num+1) == -1:
                    # This happens when an optional group does not
                    # contribute to the match. In this case there is
                    # no group to highlight.
                    continue
                start = buf.get_iter_at_line_offset(i, m.start(group_num+1))
                end = buf.get_iter_at_line_offset(i, m.end(group_num+1))
                buf.apply_tag(self.green_tag, start, end)

    def _match_text(self, buf):
        text = buf.get_text(buf.get_start_iter(), buf.get_end_iter())
        m = re.search(self.regex, text, flags=self.flags)

        if not m:
            return

        start = buf.get_iter_at_offset(m.span()[0])
        end = buf.get_iter_at_offset(m.span()[1])
        buf.apply_tag(self.red_tag, start, end)
        for group_num, g in enumerate(m.groups()):
            if m.start(group_num+1) == -1:
                # This happens when an optional group does not
                # contribute to the match. In this case there is
                # no group to highlight.
                continue
            start = buf.get_iter_at_offset(m.start(group_num+1))
            end = buf.get_iter_at_offset(m.end(group_num+1))
            buf.apply_tag(self.green_tag, start, end)


if __name__ == "__main__":
    app = RegexApp()
    gtk.main()
