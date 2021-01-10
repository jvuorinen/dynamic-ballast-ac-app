# Dynamic ballast and restrictor app for Assetto Corsa
When active, the app constantly adjusts ballast and restrictor for all connected players so that the leader gets the maximum penalty and the last one gets no penalties at all.

## Installation
1) Copy the DynamicBallast folder into AC's apps/python folder
2) Fill in the needed information into config.py
3) Activate the app in the game launcher

## Parameters
* Max ballast - Maximum ballast penalty the app can give
* Max restrictor - Maximum restrictor penalty the app can give
* Smoothing - How "spread out" the penalties are. If this is 0, the app starts to give maximum penalties right away, even if the lead is very small. On the other hand if this is at 20, the app gradually lesses the penalties given until the gap between the first and the last driver has reached 20% of the lap length.
* Calculation interval - How often the app recalculates the results
* Posting interval - How often the app posts chat messages that the server uses to make the adjustments. Increase this in case the app does not seem to actually do the adjustments.

## Notes
Currently, server's grid id's need to be manually entered into config.py for all drivers. This is because these server's id's do not seem to match car_id's. Would be nice to do this dynamically somehow.
