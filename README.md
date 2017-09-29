### Breathe Free

## Introduction

It's a common misconception that the greatest air quality concerns should be about the smog outside. Because of inadequate ventilation and chemically-treated building materials, the air inside a home or office can be up to 5 times more polluted than outdoors. This becomes a critical concern in high traffic environments, where pollutants quickly accumulate. 

I completed a data science consulting project for a sensor company in the indoor air quality space. Their product currently tracks five common pollutants in indoor environments and alerted a manager when their air had reached hazardous levels. They wanted to provide their users' with an 8-hour forecast, so a building manager had amble time to react before the air reached a hazardous state.

## The Test Case

Historical pollutant data was taken from 400 users were selected from one major metropolitan city. Each pollutant has a resolution of 15 minutes, and varies from 2 years to ~3 months of data depending on the user. Total data set is ~1 Gb. Looking at 4 separate locations below, we can see this data is going to present a challenge for traditional statistical models for several reasons..


![4_location_plot](Images/4_plot_test.png)

- Little stationarity, very unique behavioral processes (with noise) for each location.
- Regression error metrics (i.e. RMSE), that are not guaranteed to optimize the classification of toxic events.
- A large (32 * 15 min) multi-step forecast is required, and since the reading from intermediate 15 minute time-steps matter, the data cannot be smoothed into a one-step forecasting problem.

## Turning Forecasting into Classification


## Welcome to GitHub Pages

You can use the [editor on GitHub](https://github.com/Mangarella/BreatheFree/edit/master/README.md) to maintain and preview the content for your website in Markdown files.

Whenever you commit to this repository, GitHub Pages will run [Jekyll](https://jekyllrb.com/) to rebuild the pages in your site, from the content in your Markdown files.

### Markdown

Markdown is a lightweight and easy-to-use syntax for styling your writing. It includes conventions for

```markdown
Syntax highlighted code block

# Header 1
## Header 2
### Header 3

- Bulleted
- List

1. Numbered
2. List

**Bold** and _Italic_ and `Code` text

[Link](url) and ![Image](src)
```

For more details see [GitHub Flavored Markdown](https://guides.github.com/features/mastering-markdown/).

### Jekyll Themes

Your Pages site will use the layout and styles from the Jekyll theme you have selected in your [repository settings](https://github.com/Mangarella/BreatheFree/settings). The name of this theme is saved in the Jekyll `_config.yml` configuration file.

### Support or Contact

Having trouble with Pages? Check out our [documentation](https://help.github.com/categories/github-pages-basics/) or [contact support](https://github.com/contact) and we’ll help you sort it out.
