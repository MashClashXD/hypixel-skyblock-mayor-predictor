# hypixel-skyblock-mayor-predictor
Random Forest and SVM model that predicts the winner of the Hypixel Skyblock Election.

Scraped data from [here]([url](https://hypixel-skyblock.fandom.com/wiki/Module:Mayor/Elections/ApiData?action=edit)) and [here]([url](https://hypixel-skyblock.fandom.com/wiki/Module:Mayor/Elections/Data?action=edit)).

Lacks Minister perk data so it can never be extremely accurate as they play a large role in voting behaviour. If you have minister perks (ie. which perk was the minister perk for each candidate per election) please contact me!

UPDATE:
Used an algorithm to gather the probabilities of each mayor having one of their perks to be a minister perk and used that data (as well as the minister perks that I could find on the original sites I got the data from) to populate new features that have a domain of 0...1 representing the probabilities of said perk being the mayors minister perk.

I then created two random forest models with identical paramaters that were trained and cross validation tested on only the elections that occurred after the Better Mayors update (when minister perks were added). 

This would be the most practical model to use as current mayors have minister perks that greatly affect voting behaviour. 

The model without my added features had a mean accuracy of 0.548.

The model with my added features had a mean accuracy of 0.6905.
