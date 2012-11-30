#!/usr/bin/python
#

# Ejempo de uso del modulo frontend.py

MESSAGE1 = "1 Enjoy the most powerful desktop from the free software Spanish \
community.\n\n You will have at your scope the bigger set of office, \
management, design, education applications and games than you have ever \
gotten to imagine."

import frontend

if ( __name__ == '__main__' ):
  druid = frontend.FrontendInstaller()
  druid.set_progress(65, MESSAGE1, "pixmaps/snapshot1.png")
  druid.main()
  print druid.get_username()
  print druid.get_hostname()
  print druid.get_password()
