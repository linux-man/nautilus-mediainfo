#!/usr/bin/python
#coding: utf-8

import locale, os

try:
    from urllib import unquote
except ImportError:
    from urllib.parse import unquote

from gi.repository import Nautilus, GObject, Gtk

from MediaInfoDLL import *

lang = locale.getdefaultlocale()[0]
locale_path = os.path.join(os.path.dirname(__file__), "nautilus-mediainfo/locale")
locale_file = os.path.join(locale_path, lang+".csv")
if(not os.path.isfile(locale_file)):
  lang = lang.split("_")[0]
  locale_file = os.path.join(locale_path, lang+".csv")

GUI = """
<interface>
  <requires lib="gtk+" version="3.0"/>
  <object class="GtkScrolledWindow" id="mainWindow">
    <property name="visible">True</property>
    <property name="can_focus">True</property>
    <property name="hscrollbar_policy">never</property>
    <child>
      <object class="GtkViewport" id="viewport1">
        <property name="visible">True</property>
        <property name="can_focus">False</property>
        <child>
          <object class="GtkGrid" id="grid">
            <property name="visible">True</property>
            <property name="can_focus">False</property>
            <property name="vexpand">True</property>
            <property name="margin_left">8</property>
            <property name="margin_right">8</property>
            <property name="margin_top">8</property>
            <property name="margin_bottom">8</property>
            <property name="row_spacing">4</property>
            <property name="column_spacing">16</property>
          </object>
        </child>
      </object>
    </child>
  </object>
</interface>"""

class Mediainfo(GObject.GObject, Nautilus.PropertyPageProvider):

  def get_property_pages(self, files):

    if len(files) != 1:
      return

    file = files[0]
    if file.get_uri_scheme() != 'file':
      return

    if file.is_directory():
      return

    filename = unquote(file.get_uri()[7:])

    MI = MediaInfo()
    MI.Open(filename.decode("utf-8"))
    MI.Option_Static("Complete")
    MI.Option_Static("Language", "file://{}".format(locale_file))
    info = MI.Inform().splitlines()
    if len(info) < 8:
      return

    self.property_label = Gtk.Label('Media Info')
    self.property_label.show()

    self.builder = Gtk.Builder()
    self.builder.add_from_string(GUI)

    self.mainWindow = self.builder.get_object("mainWindow")
    self.grid = self.builder.get_object("grid")

    top = 0
    for line in info:
      label = Gtk.Label()
      label.set_markup("<b>" + line[:41].strip() + "</b>")
      label.set_justify(Gtk.Justification.LEFT)
      label.set_halign(Gtk.Align.START)
      label.show()
      self.grid.attach(label, 0, top, 1, 1)
      label = Gtk.Label()
      label.set_text(line[42:].strip())
      label.set_justify(Gtk.Justification.LEFT)
      label.set_halign(Gtk.Align.START)
      label.set_selectable(True)
      label.set_line_wrap(True)
      label.show()
      self.grid.attach(label, 1, top, 1, 1)
      top += 1

    return Nautilus.PropertyPage(name="NautilusPython::mediainfo", label=self.property_label, page=self.mainWindow),

