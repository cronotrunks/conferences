#!/usr/bin/python
#

import gtk.glade

xml = gtk.glade.XML('liveinstaller.glade')
accessible_file = open('accessible_file.xml', 'w')

print >>accessible_file, "<?xml version=\"1.0\">\n<glade-interface>"

for widget in xml.get_widget_prefix(""):
  print >>accessible_file, "\t<widget class=\"" + str(widget.__class__).split("'")[1] + "\" id=\"" + widget.get_name() + "\">"
  if ( widget.get_accessible().get_name() != None ):
    if ( widget.get_accessible().get_description() != None ):
      print >>accessible_file, "\t\t<accessibility name=\"" + str(widget.get_accessible().get_name()) + "\" description=\"" + str(widget.get_accessible().get_description()) + "\">"
    else:
      print >>accessible_file, "\t\t<accessibility name=\"" + str(widget.get_accessible().get_name()) + "\">"
    if ( widget.ref_accessible() ):
      counter = 0
      while ( counter < widget.get_accessible().ref_relation_set().get_n_relations() ):
        for i in widget.get_accessible().ref_relation_set().get_relation(counter).get_property('target'):
          print >>accessible_file, "\t\t\t<atk rel_type=\"" + widget.get_accessible().ref_relation_set().get_relation(counter).get_relation_type().value_nick + "\" name=\"" + str(i.get_name()) + "\" />"
        counter+=1
    print >>accessible_file, "\t\t</accessibility>"
  print >>accessible_file, "\t</widget>"

print >>accessible_file, "</glade-interface>"
