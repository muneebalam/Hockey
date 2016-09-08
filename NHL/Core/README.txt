Start by saving all three .py files in the same folder. Change the relevant fields near the top of GetPbP, PbPMethods2, and ChartMethods (including MAX_SEASON).

Open up a text file in the same folder as GetPbP and write the following code.

import GetPbP
GetPbP.autoupdate(True)

Save the file under any name, but change the extension to .py.

Open up command line or terminal. Navigate (using the cd command) to this folder. Write

python3 [name].py

where [name] is the name of the file you just wrote and saved. 

It will take a long time to run (and make sure you have at least 25 GB of free disk space), but should give you all preseason, regular season, and playoff games from 2007 to the present in CSVs, both individual games and team logs (all a team's games in a single file).

Credits:

Ice rink, from @alexgoogs: https://github.com/war-on-ice/icerink

Team colors, from http://teamcolors.arc90.com/ via @joewillage https://github.com/jwillage/Hockey/blob/master/Hockey/eventPlot.R


