# Fantasy Football Draft Projection
**Predicting a player's fantasy football success from their historical performance for pre-draft ranking**

**Language:** Python (pandas, sklearn, seaborn, numpy) <br/>
**Software:** Tableau

The goal was the predict a player's fantasy performance in an upcoming year by using only their historical performance. Player's football stats and fantasy scores are scraped from [Pro Football Reference](https://www.pro-football-reference.com/years/2000/fantasy.htm) from the years 2000 - 2019 and datasets of player's performance from 2 - 4 years back were cleaned and formatted (years back adjustable).

Therefore, each row of the dataset contains a player's fantasy points during the year and stats from prior years. This allows a player to be represented multiple times but removes rookie years and years below 8 games played to remove injuries or non-relevant fantasy players.

When picking models, K-Nearest-Neighbor, Random Forest Regression, Elastic Net (Linear Regression), and Ensembled model from RFR / EN-LR were compared. The models aimed to predict the fantasy scores per game over the season and scored using root square mean error (RSME) when comparing hyperparameters.

However, to have a more comparative metric, the prediction output was converted to rankings per position and compared to professional forecasting rankings for the upcoming season (consensus from [Fantasy Pros](https://www.fantasypros.com/)). The outputs would be compared against the actual rankings which were derived from the actual fantasy points per game of the season.

The results are summarized in the links below, with the data manipulation in the first notebook, modeling and scoring in the second, and a tableau storyboard for visualization and summary of the data.

- **Notebook 1:** [Feature Extraction and Data Formatting](https://github.com/albechen/fantasyfootball-draft-projection/blob/master/ff-1-feature_extract_clean.ipynb)
- **Notebook 2:** [Model Evaluations and Predictions](https://github.com/albechen/fantasyfootball-draft-projection/blob/master/ff-2-model_predict_score.ipynb)
- **Tableau:** [Visualization Summary](https://public.tableau.com/profile/a.chen#!/vizhome/ff-tableau-summary/FINALStoryBoard)

## Tableau Sample:
![alt text](/images/Picture1.png "postion_stats")
![alt text](/images/Picture5.png "model_selection")
![alt text](/images/Picture4.png "2020_Predictions")
