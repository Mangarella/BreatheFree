# Breathe Free

## Introduction

It's a common misconception that the most polluted air is the smog outside. Inadequate ventilation, chemically-treated building materials, and high traffic areas can commonly cause the air inside a home or office can be up to 5 times more polluted than outdoors. 

As part of Insight Data Science, I completed a data science consulting project for a sensor company in the indoor air quality space. Their product tracks five pollutants in indoor environments and alerts occupants when a pollutant had reached hazardous levels. However, currently they can only alert occupants **at the last minute**. They wanted to provide their users' with an 8-hour warning, so there was amble time to take measures (by increasing ventilation, disinfecting surfaces, etc.) **before it's too late.**

## The Data and Challenge for Traditional Time Series Forecasting

Historical pollutant data, user data, and location data was accessed from the company's databases through Google BigQuery. As a test case, data was taken from 400 users in a major metropolitan city for a harmful gas that will be anonymously refered to as **Pollutant A**. Each pollutant has a resolution of 15 minutes, and historical data goes back up to 2 years for each user. Looking at a weeks worth of data for 4 separate locations below, we can see that predicting if **Pollutant A** is going to cross into the danger zone (seen in red) will be very challenging for traditional statistical time series forecasting models. 

<div style="text-align:center"><img src ="Images/4_plot_test.png" /></div>

Most time series forecasting relies on the assumption that the time series is stationary, meaning that the mean, standard deviation, and autocorrelation (correlation to previous time points) are constant for some periodic measure of time. I could go through the trouble to de-season and de-trend the data into a stationary time series, but I would quickly hit another roadblock:


Insert time series forecast image here

A traditional time series model is a regression model, and the parameters of any interesting statistical model (ARIMA, ARMAX, etc.) are fit on the basis of minimizing a cost function (such as least squares) and this minimization is not guaranteed to optimize for the classification of toxic events.

Lastly, A large (32 * 15 min = 8 hours) multi-step forecast is required, and since I need to know if **any** future 15 minute interval hits an unsafe range, the data cannot be smoothed into a one-step forecasting problem.


## Turning Time Series Forecasting into Generalized Classification

On a very high level, this is likely unique behavioral processes (with noise) for each location.



## About Me

My name is Michael Mangarella (Mike). I'm a chemical engineer and data scientist. I received my PhD in Chemical and Biomolecular Engineering from Georgia Tech in 2015, and spent the last year running a startup to turn gas filtration technology from my dissertation into viable military grade gas filters. Most of my passion for data science comes from my minor in quantitative finance, and a couple years developing retail options trading strategies. I joined Insight in Fall 2017 to continue my technical development. 
