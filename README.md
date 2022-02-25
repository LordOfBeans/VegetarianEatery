This is a bit of code I wrote in an attempt to find healthy vegetarian food in the Eatery, which is the University of Pittsburgh's dining hall.
This is a work in progress and currently relies on brute forcing, which is not nearly fast enough to make a 2000-calorie meal plan for an entire day.
There are also some other optimizations that could be made, but they would not have much of an effect in the grand scheme of things until I find a way around brute forcing.
I am currently looking at implementing methods like simulated annealing.

When you run TheEatery.py, it will make requests to Pitt's dining website, which it then converts into a more useful format. Then it prints the best combinations as it find them.
There are a lot of improvements to be made.
