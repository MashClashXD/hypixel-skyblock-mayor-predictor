# hypixel-skyblock-mayor-predictor
Iterative Random Forest (iRF) and SVM model that predicts the winner of the Hypixel Skyblock Election.

Scraped data from [here]([url](https://hypixel-skyblock.fandom.com/wiki/Module:Mayor/Elections/ApiData?action=edit)) and [here]([url](https://hypixel-skyblock.fandom.com/wiki/Module:Mayor/Elections/Data?action=edit)).

Lacks Minister perk data so it can never be extremely accurate as they play a large role in voting behaviour. If you have minister perks (ie. which perk was the minister perk for each candidate per election) please contact me!

UPDATE:
Used an algorithm to gather the probabilities of each mayor having one of their perks to be a minister perk and used that data (as well as the minister perks that I could find on the original sites I got the data from) to populate new features that have a domain of 0...1 representing the probabilities of said perk being the mayors minister perk.

I then created two random forest models with identical paramaters that were trained and cross validation tested on only the elections that occurred after the Better Mayors update (when minister perks were added). 

This would be the most practical model to use as current mayors have minister perks that greatly affect voting behaviour. 

The model without my added features had a mean accuracy of 0.548.

The model with my added features had a mean accuracy of 0.6905.

UPDATE 2:

Attempted to create an iterative random forest model to better predict election winners.

To reduce bias I decided to use the entire dataset for this model.

While in comparison to the random forest model with only data from after the better mayors update (after july 3rd 2024) it is less accurate, in comparison to a basic RF model with the same data its more accurate, yet still less accurate than the limited data model.

While in most cases this may make this new iRF model useless, I believe it isnt. 

The reason the iRF model is less accurate is due to a lack of minister data on all elections before july 3rd 2024, forcing the perk and candidate features to take on extra importance. On top of this adding the iterative nature of an iRF model compounds these effects.

However, despite these flaws; in modern cases I believe this is the best model to use in future elections for predictions. 

This is because when we look at the feature list for the iRF model we can see that the features are much more robust and make more logical sense.

for example, 

the #1 feature for RF = Perks.EZPZ  - 0.052568 

the #1 feature for iRF = interaction_perk_Perks.PetXPBuff * perk_Perks.MythologicalRitual - 0.022024

The fact that the RF has given nearly 2 times the weight as the iRF on a single perk means that its heavily susceptible to bias from a single perk when in reality most people dont think in terms of single perks.

On the other hand, the iRF model's #1 feature is the interaction of two perks from Diana  (this is also weighted half as much as the RFs #1). Showing that it understands more closely how real players may think when voting, since a player will often weigh combinations of perks vs other single/combos of perks in their head before voting.

This is another reason as to why this model is very terribly affected by a lack of data. By lacking data it means we also lack many interactions between specific perks such as when Mining Festival and Mythological Ritual perks are simultaneously in the election.

There isnt much currently that I can do to improve this model much due to lack of data. As more data comes to existence its possible the model may become slightly better hopefully.

If my logic as to why the predictor is less accurate is correct, it is possible that as more data is added it will rapidly become more accurate as its able to find more data to help validate minister perk importance, solidify its understanding of the most important mayor perks and find niche interactions between unrelated perks (this is what would make the model potenially better than humans).

However, it is still limited greatly by a lack of minister data in total and a lack of quality minister data (a majority of it is synthesized with probabilities).

In all, through this project I've come to the conclusion that while its possible to create a somewhat accurate predictor for hypixel skyblock mayors, it will continue to be quite inaccurate due to a lack of data.

Likely done with project till further notice.

